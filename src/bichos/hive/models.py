"""Orchestrator data models for the bichos hive layer.

This module defines:
- SwarmState  — mutable state dataclass threaded through pydantic_graph workflow nodes
- SummaryStats    — Pydantic model for aggregate analysis statistics
- ReportMetadata  — Pydantic model for report provenance
- AnalysisReport  — Pydantic model for the immutable final output of a swarm run
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, Field, field_validator

from bichos.agents.ant.models import BugReport, ExplorationResult
from bichos.config import HiveConfig
from bichos.graph.models import CodeGraph
from bichos.stigmergy.cache import PheromoneCache


@dataclass
class SwarmState:
    """Mutable state passed through pydantic_graph workflow nodes.

    Attributes:
        code_graph:       Static call-graph of the analysed codebase.
        pheromone_cache:  Shared persistent pheromone grid.
        config:           Top-level hive configuration.
        results:          Exploration results collected from ant agents.
        degraded_agents:  IDs of ant agents that errored during the run.
    """

    code_graph: CodeGraph
    pheromone_cache: PheromoneCache
    config: HiveConfig
    results: list[ExplorationResult] = field(default_factory=list)
    degraded_agents: list[str] = field(default_factory=list)


# ── Nested models ─────────────────────────────────────────────────────────────


class SummaryStats(BaseModel):
    """Aggregate statistics from a completed swarm analysis run.

    Attributes:
        total_functions_visited: Number of unique functions visited across all ants.
        total_bugs_found:        Total bug reports (may include duplicates).
        unique_bugs:             De-duplicated bug count.
        avg_confidence:          Mean model confidence across all bug reports.
    """

    total_functions_visited: int = Field(..., ge=0)
    total_bugs_found: int = Field(..., ge=0)
    unique_bugs: int = Field(..., ge=0)
    avg_confidence: float = Field(..., ge=0.0, le=1.0)


class ReportMetadata(BaseModel):
    """Provenance metadata attached to an AnalysisReport.

    Attributes:
        repo_path:    Absolute or relative path to the analysed repository.
        agent_count:  Number of ant agents that participated in the run (>= 1).
        timestamp:    ISO-8601 timestamp string for when the report was produced.
        total_tokens: Total LLM tokens consumed across all agents.
    """

    repo_path: str
    agent_count: int = Field(..., ge=1)
    timestamp: str
    total_tokens: int = Field(..., ge=0)


# ── Top-level report ──────────────────────────────────────────────────────────


class AnalysisReport(BaseModel):
    """Immutable final output produced by the hive orchestrator.

    Attributes:
        bugs:               Deduplicated, filtered list of bug findings.
        summary_stats:      Aggregate statistics for the run.
        pheromone_heatmap:  Mapping of function qualified name → pheromone
                            intensity in [0.0, 100.0].
        metadata:           Report provenance information.
    """

    bugs: list[BugReport]
    summary_stats: SummaryStats
    pheromone_heatmap: dict[str, float]
    metadata: ReportMetadata

    @field_validator("pheromone_heatmap")
    @classmethod
    def _validate_heatmap_intensities(
        cls, heatmap: dict[str, float]
    ) -> dict[str, float]:
        """Ensure every intensity value is within [0.0, 100.0]."""
        for fn_name, intensity in heatmap.items():
            if not (0.0 <= intensity <= 100.0):
                raise ValueError(
                    f"pheromone_heatmap[{fn_name!r}] = {intensity} is outside "
                    f"the valid intensity range [0.0, 100.0]"
                )
        return heatmap
