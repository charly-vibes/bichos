"""Tests for agents/ant/agent.py — forager agent and run_ant entry point."""

from __future__ import annotations

import asyncio
import os
import random
from pathlib import Path

import networkx as nx
import pytest
from pydantic_ai.models.test import TestModel

from bichos.agents.ant.agent import forager, run_ant
from bichos.agents.ant.models import AntDeps, BugReport, ExplorationResult
from bichos.config import HiveConfig, ModelConfig
from bichos.graph.models import CodeGraph, NodeMeta
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import BugPheromone, PheromoneType

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def _node(
    name: str,
    file_path: str = "mod.py",
    lineno: int = 1,
    loc: int = 10,
    complexity: int = 2,
) -> NodeMeta:
    return NodeMeta(
        name=name,
        qualified_name=name,
        file_path=file_path,
        lineno=lineno,
        loc=loc,
        complexity=complexity,
    )


def _make_graph_with_nodes(
    nodes: dict[str, NodeMeta], edges: list[tuple[str, str]]
) -> CodeGraph:
    g = nx.DiGraph()
    for qname, meta in nodes.items():
        g.add_node(qname, meta=meta)
    for src, dst in edges:
        g.add_edge(src, dst)
    return CodeGraph(graph=g, root=Path("/fake/root"))


def _make_simple_ant_deps(tmp_path: Path, semaphore_limit: int = 1) -> AntDeps:
    """Build AntDeps with a multi-node graph and a test-compatible model string."""
    nodes = {
        "mod.func_a": _node("func_a", file_path="mod.py", lineno=1, complexity=3),
        "mod.func_b": _node("func_b", file_path="mod.py", lineno=20, complexity=7),
        "mod.func_c": _node("func_c", file_path="mod.py", lineno=40, complexity=5),
    }
    graph = _make_graph_with_nodes(
        nodes,
        [("mod.func_a", "mod.func_b"), ("mod.func_b", "mod.func_c")],
    )
    cache = PheromoneCache(cache_dir=tmp_path / "cache")
    # Use 'test' so that forager.run(model=deps.config.ant_model) resolves and
    # the override(model=TestModel(...)) can replace it during testing.
    config = HiveConfig(model=ModelConfig(provider="openai", name="test"))
    return AntDeps(
        pheromone_cache=cache,
        code_graph=graph,
        config=config,
        rng=random.Random(42),
        llm_semaphore=asyncio.Semaphore(semaphore_limit),
    )


# ---------------------------------------------------------------------------
# Guard test — pydantic_ai private attribute contract
# ---------------------------------------------------------------------------


def test_override_model_attr_exists() -> None:
    """Guard: pydantic_ai Agent must expose _override_model as a ContextVar.

    agent.py relies on forager._override_model.get() to detect test overrides
    (pydantic_ai Agent._override_model, agent/__init__.py:403).  This test
    will fail loudly if a pydantic_ai upgrade renames or removes the attribute,
    prompting a fix to the eager-evaluation guard in run_ant().
    """
    from contextvars import ContextVar

    assert hasattr(forager, "_override_model"), (
        "pydantic_ai Agent no longer has _override_model; update run_ant() guard"
    )
    assert isinstance(forager._override_model, ContextVar), (
        "_override_model is no longer a ContextVar; update run_ant() guard"
    )


# ---------------------------------------------------------------------------
# Unit tests — ExplorationResult model
# ---------------------------------------------------------------------------


def test_exploration_result_is_valid_pydantic_model() -> None:
    """ExplorationResult must be a Pydantic model with correct field types."""
    result = ExplorationResult(
        path_visited=["mod.func_a", "mod.func_b"],
        bugs_found=[],
        tokens_used=5,
    )
    assert isinstance(result.path_visited, list)
    assert all(isinstance(s, str) for s in result.path_visited)
    assert isinstance(result.bugs_found, list)
    assert isinstance(result.tokens_used, int)
    assert result.tokens_used == 5
    assert result.bugs_found == []


def test_exploration_result_defaults_tokens_used_to_zero() -> None:
    """tokens_used should default to 0 when not provided."""
    result = ExplorationResult(path_visited=[], bugs_found=[])
    assert result.tokens_used == 0


def test_bug_report_has_correct_field_types() -> None:
    """BugReport must validate field types and constraints."""
    report = BugReport(
        function_name="mod.func_a",
        file_path="mod.py",
        line_number=10,
        description="Off-by-one error",
        severity=5,
        confidence=0.85,
    )
    assert isinstance(report.function_name, str)
    assert isinstance(report.file_path, str)
    assert isinstance(report.line_number, int)
    assert isinstance(report.description, str)
    assert isinstance(report.severity, int)
    assert isinstance(report.confidence, float)


# ---------------------------------------------------------------------------
# Unit tests — run_ant with TestModel
# ---------------------------------------------------------------------------


async def test_forager_returns_exploration_result(tmp_path: Path) -> None:
    """run_ant must return an ExplorationResult when TestModel is used."""
    deps = _make_simple_ant_deps(tmp_path)
    with forager.override(
        model=TestModel(
            call_tools=[],
            custom_output_args={
                "path_visited": ["mod.func_a", "mod.func_b"],
                "bugs_found": [],
                "tokens_used": 0,
            },
        )
    ):
        result = await run_ant(deps)

    assert isinstance(result, ExplorationResult)
    assert result.path_visited == ["mod.func_a", "mod.func_b"]
    assert result.bugs_found == []


async def test_forager_visits_multiple_nodes(tmp_path: Path) -> None:
    """Agent must return a path_visited list with more than one entry."""
    deps = _make_simple_ant_deps(tmp_path)
    with forager.override(
        model=TestModel(
            call_tools=[],
            custom_output_args={
                "path_visited": ["mod.func_a", "mod.func_b", "mod.func_c"],
                "bugs_found": [],
                "tokens_used": 0,
            },
        )
    ):
        result = await run_ant(deps)

    assert len(result.path_visited) > 1


async def test_forager_reports_bug_above_threshold(tmp_path: Path) -> None:
    """When run_ant is called with a bug above threshold, pheromone is deposited.

    This test directly calls report_bug via its tool function (bypassing the LLM)
    to verify that the pheromone deposit side-effect works end-to-end.
    """
    from unittest.mock import MagicMock

    from bichos.agents.ant.tools import report_bug

    deps = _make_simple_ant_deps(tmp_path)
    ctx = MagicMock()
    ctx.deps = deps

    # confidence >= 0.7 (default min_confidence) and severity >= 3
    outcome = await report_bug(
        ctx,
        function_name="mod.func_b",
        description="Null pointer dereference",
        severity=5,
        confidence=0.9,
    )

    assert "deposited" in outcome.lower() or "reported" in outcome.lower()
    stored = deps.pheromone_cache.get("bug:mod.func_b")
    assert stored is not None
    assert isinstance(stored, BugPheromone)

    # Now run_ant with TestModel to confirm ExplorationResult also works
    with forager.override(
        model=TestModel(
            call_tools=[],
            custom_output_args={
                "path_visited": ["mod.func_a", "mod.func_b"],
                "bugs_found": [],
                "tokens_used": 0,
            },
        )
    ):
        result = await run_ant(deps)

    # The pheromone is still there from before
    assert deps.pheromone_cache.get("bug:mod.func_b") is not None
    assert isinstance(result, ExplorationResult)


async def test_forager_concurrent_runs(tmp_path: Path) -> None:
    """Three concurrent run_ant calls must all complete without error."""
    deps1 = _make_simple_ant_deps(tmp_path / "d1", semaphore_limit=3)
    deps2 = _make_simple_ant_deps(tmp_path / "d2", semaphore_limit=3)
    deps3 = _make_simple_ant_deps(tmp_path / "d3", semaphore_limit=3)

    with forager.override(
        model=TestModel(
            call_tools=[],
            custom_output_args={
                "path_visited": ["mod.func_a", "mod.func_b"],
                "bugs_found": [],
                "tokens_used": 0,
            },
        )
    ):
        results = await asyncio.gather(
            run_ant(deps1),
            run_ant(deps2),
            run_ant(deps3),
        )

    assert len(results) == 3
    assert all(isinstance(r, ExplorationResult) for r in results)
    assert all(len(r.path_visited) > 0 for r in results)


async def test_forager_handles_dead_end(tmp_path: Path) -> None:
    """A single-node graph (dead end) must be handled gracefully."""
    nodes = {"solo.func": _node("func", file_path="solo.py", lineno=1, complexity=1)}
    graph = _make_graph_with_nodes(nodes, [])
    cache = PheromoneCache(cache_dir=tmp_path / "cache")
    config = HiveConfig(model=ModelConfig(provider="openai", name="test"))
    deps = AntDeps(
        pheromone_cache=cache,
        code_graph=graph,
        config=config,
        rng=random.Random(0),
        llm_semaphore=asyncio.Semaphore(1),
    )

    with forager.override(
        model=TestModel(
            call_tools=[],
            custom_output_args={
                "path_visited": ["solo.func"],
                "bugs_found": [],
                "tokens_used": 0,
            },
        )
    ):
        result = await run_ant(deps, start_function="solo.func")

    assert isinstance(result, ExplorationResult)
    assert result.path_visited == ["solo.func"]


# ---------------------------------------------------------------------------
# report_bug threshold behaviour — no LLM needed
# ---------------------------------------------------------------------------


async def test_report_bug_does_not_deposit_when_confidence_below_threshold(
    tmp_path: Path,
) -> None:
    """report_bug must NOT deposit pheromone when confidence < min_confidence."""
    from unittest.mock import MagicMock

    from bichos.agents.ant.tools import report_bug

    deps = _make_simple_ant_deps(tmp_path)
    ctx = MagicMock()
    ctx.deps = deps

    # confidence=0.3 < 0.7 (default min_confidence)
    outcome = await report_bug(
        ctx,
        function_name="mod.func_a",
        description="Possible issue",
        severity=4,
        confidence=0.3,
    )

    assert (
        "below" in outcome.lower()
        or "threshold" in outcome.lower()
        or "logged" in outcome.lower()
    )
    assert deps.pheromone_cache.get("bug:mod.func_a") is None


async def test_report_bug_does_not_deposit_when_severity_below_threshold(
    tmp_path: Path,
) -> None:
    """report_bug must NOT deposit pheromone when severity < 3."""
    from unittest.mock import MagicMock

    from bichos.agents.ant.tools import report_bug

    deps = _make_simple_ant_deps(tmp_path)
    ctx = MagicMock()
    ctx.deps = deps

    # severity=2 < 3 minimum
    outcome = await report_bug(
        ctx,
        function_name="mod.func_a",
        description="Trivial style issue",
        severity=2,
        confidence=0.95,
    )

    assert (
        "below" in outcome.lower()
        or "threshold" in outcome.lower()
        or "logged" in outcome.lower()
    )
    assert deps.pheromone_cache.get("bug:mod.func_a") is None


# ---------------------------------------------------------------------------
# Integration test (slow — requires OPENAI_API_KEY)
# ---------------------------------------------------------------------------


@pytest.mark.slow
async def test_run_ant_integration_finds_bugs(
    simple_bugs_path: Path, tmp_path: Path
) -> None:
    """run_ant on simple_bugs fixture with a real model finds at least one bug.

    Requires OPENAI_API_KEY environment variable to be set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")

    from bichos.graph.builder import build_code_graph

    code_graph = build_code_graph(root=simple_bugs_path)

    cache = PheromoneCache(cache_dir=tmp_path / "cache")
    config = HiveConfig.default()
    deps = AntDeps(
        pheromone_cache=cache,
        code_graph=code_graph,
        config=config,
        rng=random.Random(99),
        llm_semaphore=asyncio.Semaphore(1),
    )

    result = await run_ant(deps)

    assert isinstance(result, ExplorationResult)
    assert len(result.bugs_found) >= 1, (
        "Expected at least one bug in simple_bugs fixture"
    )
    # Pheromone cache should have entries for found bugs
    bug_pheromones = list(cache.iter_by_type(PheromoneType.BUG))
    assert len(bug_pheromones) >= 1, "Expected pheromone entries after run"
