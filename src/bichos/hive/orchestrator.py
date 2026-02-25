"""Hive orchestrator — pydantic_graph workflow for the bichos swarm analysis.

This module implements the four-node pipeline:

    InitNode → SplitNode → JoinNode → ReportNode → End(AnalysisReport)

The public entry point is :func:`run_hive`.
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import networkx as nx
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from bichos.agents.ant.agent import run_ant
from bichos.agents.ant.models import AntDeps, BugReport, ExplorationResult
from bichos.config import HiveConfig
from bichos.graph.builder import build_code_graph
from bichos.graph.models import CodeGraph
from bichos.hive.models import (
    AnalysisReport,
    ReportMetadata,
    SummaryStats,
    SwarmState,
)
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import PheromoneType

# ---------------------------------------------------------------------------
# Timeout applied to every individual ant agent call (seconds)
# ---------------------------------------------------------------------------
_AGENT_TIMEOUT: float = 300.0


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------


@dataclass
class InitNode(BaseNode[SwarmState, None, None]):
    """Build CodeGraph and PheromoneCache, store them on *SwarmState*.

    Accepts *repo_path* and *cache_dir* as node-level parameters so that
    the graph entry point can be driven by the caller without pre-populating
    SwarmState (which requires a CodeGraph + PheromoneCache to construct).
    """

    repo_path: Path
    cache_dir: Path | None = None

    async def run(self, ctx: GraphRunContext[SwarmState, None]) -> SplitNode:
        """Build graph + cache, mutate ctx.state, return SplitNode."""
        config = ctx.state.config

        # Build code graph
        ctx.state.code_graph = build_code_graph(self.repo_path, config.max_files)

        # Determine cache directory (deterministic hash per repo_path)
        if self.cache_dir is not None:
            cache_dir = self.cache_dir
        else:
            repo_hash = hashlib.sha1(str(self.repo_path).encode()).hexdigest()[:8]
            cache_dir = Path(f"/tmp/bichos-{repo_hash}")

        ctx.state.pheromone_cache = PheromoneCache(
            cache_dir=cache_dir,
            rho=config.aco.rho,
            max_intensity=config.stigmergy.max_intensity,
            min_intensity=config.stigmergy.min_intensity,
        )

        return SplitNode()


@dataclass
class SplitNode(BaseNode[SwarmState, None, None]):
    """Spawn one AntForagerAgent per function node, gather results concurrently."""

    async def run(self, ctx: GraphRunContext[SwarmState, None]) -> JoinNode:
        """Run all ant agents and collect results / degraded agent IDs."""
        state = ctx.state
        config = state.config

        # Collect all non-class nodes as starting points
        function_nodes = [
            (qname, meta)
            for qname, meta in state.code_graph.all_nodes()
            if not meta.is_class
        ]

        semaphore = asyncio.Semaphore(config.ant_count)

        async def _run_one(qname: str) -> ExplorationResult:
            deps = AntDeps(
                pheromone_cache=state.pheromone_cache,
                code_graph=state.code_graph,
                config=config,
                rng=random.Random(),
                llm_semaphore=semaphore,
            )
            return await asyncio.wait_for(
                run_ant(deps, start_function=qname),
                timeout=_AGENT_TIMEOUT,
            )

        tasks = [_run_one(qname) for qname, _ in function_nodes]
        outcomes: list[ExplorationResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        for idx, outcome in enumerate(outcomes):
            if isinstance(outcome, BaseException):
                agent_id = f"ant-{idx}"
                state.degraded_agents.append(agent_id)
            else:
                state.results.append(outcome)

        return JoinNode()


@dataclass
class JoinNode(BaseNode[SwarmState, None, None]):
    """Deduplicate bugs by (file_path, line_number) keeping highest confidence."""

    async def run(self, ctx: GraphRunContext[SwarmState, None]) -> ReportNode:
        """Deduplicate all bugs and pass the list forward to ReportNode."""
        all_bugs: list[BugReport] = []
        for result in ctx.state.results:
            all_bugs.extend(result.bugs_found)

        # Dedup: keep highest-confidence bug per (file_path, line_number)
        best: dict[tuple[str, int], BugReport] = {}
        for bug in all_bugs:
            key = (bug.file_path, bug.line_number)
            existing = best.get(key)
            if existing is None or bug.confidence > existing.confidence:
                best[key] = bug

        deduplicated = list(best.values())
        return ReportNode(
            deduplicated_bugs=deduplicated,
            repo_path=ctx.state.code_graph.root,
        )


@dataclass
class ReportNode(BaseNode[SwarmState, None, AnalysisReport]):
    """Build AnalysisReport from aggregated SwarmState data."""

    deduplicated_bugs: list[BugReport]
    repo_path: Path

    async def run(self, ctx: GraphRunContext[SwarmState, None]) -> End[AnalysisReport]:
        """Compute statistics, build heatmap, return End(AnalysisReport)."""
        state = ctx.state
        results = state.results

        # Aggregate statistics
        total_functions_visited = sum(len(r.path_visited) for r in results)
        total_bugs_found = sum(len(r.bugs_found) for r in results)
        unique_bugs = len(self.deduplicated_bugs)
        all_confidences = [b.confidence for r in results for b in r.bugs_found]
        avg_confidence = (
            sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        )
        total_tokens = sum(r.tokens_used for r in results)

        summary_stats = SummaryStats(
            total_functions_visited=total_functions_visited,
            total_bugs_found=total_bugs_found,
            unique_bugs=unique_bugs,
            avg_confidence=avg_confidence,
        )

        # Build pheromone heatmap from BUG pheromones in the cache
        heatmap: dict[str, float] = {}
        for pheromone in state.pheromone_cache.iter_by_type(PheromoneType.BUG):
            location = pheromone.function_name  # type: ignore[union-attr]
            intensity = min(100.0, max(0.0, pheromone.intensity))
            if location in heatmap:
                heatmap[location] = min(100.0, heatmap[location] + intensity)
            else:
                heatmap[location] = intensity

        metadata = ReportMetadata(
            repo_path=str(self.repo_path),
            agent_count=max(1, len(results) + len(state.degraded_agents)),
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            total_tokens=total_tokens,
        )

        report = AnalysisReport(
            bugs=self.deduplicated_bugs,
            summary_stats=summary_stats,
            pheromone_heatmap=heatmap,
            metadata=metadata,
        )
        return End(report)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


async def run_hive(repo_path: Path, config: HiveConfig) -> AnalysisReport:
    """Run the full bichos swarm analysis pipeline.

    Args:
        repo_path: Root directory of the repository to analyse.
        config:    Top-level hive configuration.

    Returns:
        An :class:`~bichos.hive.models.AnalysisReport` summarising all findings.
    """
    # Build placeholder state; InitNode will replace code_graph and pheromone_cache.
    placeholder_graph = CodeGraph(graph=nx.DiGraph(), root=repo_path)
    # Use a temporary cache dir as placeholder; InitNode overwrites it.
    repo_hash = hashlib.sha1(str(repo_path).encode()).hexdigest()[:8]
    placeholder_cache_dir = Path(f"/tmp/bichos-placeholder-{repo_hash}")
    placeholder_cache = PheromoneCache(
        cache_dir=placeholder_cache_dir,
        rho=config.aco.rho,
        max_intensity=config.stigmergy.max_intensity,
        min_intensity=config.stigmergy.min_intensity,
    )

    state = SwarmState(
        code_graph=placeholder_graph,
        pheromone_cache=placeholder_cache,
        config=config,
    )

    # Nodes have heterogeneous RunEndT; cast to satisfy Graph's homogeneous type param.
    _nodes = cast(
        "list[type[BaseNode[SwarmState, None, AnalysisReport]]]",
        [InitNode, SplitNode, JoinNode, ReportNode],
    )
    graph: Graph[SwarmState, None, AnalysisReport] = Graph(nodes=_nodes)
    _start: BaseNode[SwarmState, None, AnalysisReport] = cast(
        "BaseNode[SwarmState, None, AnalysisReport]",
        InitNode(repo_path=repo_path),
    )
    result = await graph.run(_start, state=state)
    return result.output
