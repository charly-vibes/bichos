"""Tests for agents/ant/tools.py — forager tool functions."""

from __future__ import annotations

import asyncio
import random
from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest

from bichos.agents.ant.models import AntDeps
from bichos.config import HiveConfig
from bichos.graph.models import CodeGraph, NodeMeta
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import BugPheromone

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def _make_graph_with_nodes(
    nodes: dict[str, NodeMeta], edges: list[tuple[str, str]]
) -> CodeGraph:
    """Build a CodeGraph from a dict of NodeMeta objects and a list of edges."""
    g = nx.DiGraph()
    for qname, meta in nodes.items():
        g.add_node(qname, meta=meta)
    for src, dst in edges:
        g.add_edge(src, dst)
    return CodeGraph(graph=g, root=Path("/fake/root"))


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


@pytest.fixture()
def hive_config() -> HiveConfig:
    return HiveConfig.default()


@pytest.fixture()
def ant_deps(tmp_path: Path, hive_config: HiveConfig) -> AntDeps:
    """Minimal AntDeps with a simple two-node code graph."""
    nodes = {
        "mod.func_a": _node("func_a", file_path="mod.py", lineno=1, complexity=3),
        "mod.func_b": _node("func_b", file_path="mod.py", lineno=20, complexity=7),
    }
    graph = _make_graph_with_nodes(nodes, [("mod.func_a", "mod.func_b")])
    cache = PheromoneCache(cache_dir=tmp_path / "cache")
    return AntDeps(
        pheromone_cache=cache,
        code_graph=graph,
        config=hive_config,
        rng=random.Random(42),
        llm_semaphore=asyncio.Semaphore(1),
    )


# ---------------------------------------------------------------------------
# Fake RunContext
# ---------------------------------------------------------------------------


def _make_ctx(deps: AntDeps) -> MagicMock:
    """Create a minimal mock RunContext that tools can use via ctx.deps."""
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


# ---------------------------------------------------------------------------
# choose_next_function
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_choose_next_function_picks_weighted_neighbor(
    ant_deps: AntDeps,
) -> None:
    """choose_next_function must return a valid neighbor of the current node."""
    # Pre-seed a high pheromone on func_b so it dominates selection.
    bug = BugPheromone(
        key="bug:mod.func_b",
        depositor="ant-test",
        severity=5,
        file_path="mod.py",
        function_name="mod.func_b",
        description="test",
        intensity=80.0,
        confidence=0.9,
    )
    ant_deps.pheromone_cache.deposit(bug)

    from bichos.agents.ant.tools import choose_next_function

    ctx = _make_ctx(ant_deps)
    result = await choose_next_function(ctx, "mod.func_a")
    # func_a has only one neighbor: func_b
    assert result == "mod.func_b"


@pytest.mark.asyncio
async def test_choose_next_function_returns_current_at_dead_end(
    ant_deps: AntDeps,
) -> None:
    """When a node has no outgoing neighbors, the current node is returned."""
    from bichos.agents.ant.tools import choose_next_function

    ctx = _make_ctx(ant_deps)
    # func_b has no successors in our graph fixture
    result = await choose_next_function(ctx, "mod.func_b")
    assert result == "mod.func_b"


# ---------------------------------------------------------------------------
# analyze_code
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analyze_code_returns_snippet(
    tmp_path: Path, hive_config: HiveConfig
) -> None:
    """analyze_code must return a snippet containing metadata and source lines."""
    # Write a real source file so analyze_code can read it.
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    src_file = src_dir / "example.py"
    lines = [f"# line {i}\n" for i in range(1, 51)]
    src_file.write_text("".join(lines))

    nodes = {
        "example.my_func": NodeMeta(
            name="my_func",
            qualified_name="example.my_func",
            file_path="src/example.py",
            lineno=25,
            loc=10,
            complexity=3,
        )
    }
    graph = _make_graph_with_nodes(nodes, [])
    # Root must be tmp_path so that root / file_path resolves correctly.
    graph_with_root = CodeGraph(graph=graph.graph, root=tmp_path)
    cache = PheromoneCache(cache_dir=tmp_path / "cache")
    deps = AntDeps(
        pheromone_cache=cache,
        code_graph=graph_with_root,
        config=hive_config,
        rng=random.Random(0),
        llm_semaphore=asyncio.Semaphore(1),
    )

    from bichos.agents.ant.tools import analyze_code

    ctx = _make_ctx(deps)
    snippet = await analyze_code(ctx, "example.my_func")

    assert (
        "example.my_func" in snippet
        or "my_func" in snippet
        or "src/example.py" in snippet
    )
    # Should contain a line number reference.
    assert "25" in snippet


@pytest.mark.asyncio
async def test_analyze_code_unknown_function(ant_deps: AntDeps) -> None:
    """analyze_code must return a graceful message for unknown function names."""
    from bichos.agents.ant.tools import analyze_code

    ctx = _make_ctx(ant_deps)
    result = await analyze_code(ctx, "nonexistent.func")
    assert "not found" in result.lower() or "nonexistent" in result


# ---------------------------------------------------------------------------
# report_bug
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_report_bug_deposits_pheromone_when_above_threshold(
    ant_deps: AntDeps,
) -> None:
    """Deposit a BugPheromone when confidence >= min_confidence and severity >= 3."""
    from bichos.agents.ant.tools import report_bug

    ctx = _make_ctx(ant_deps)
    # Default min_confidence is 0.7; we use 0.9 and severity 4.
    result = await report_bug(
        ctx, "mod.func_a", "Off-by-one error", severity=4, confidence=0.9
    )

    assert "deposited" in result.lower() or "reported" in result.lower()
    # Verify pheromone was actually written to the cache.
    stored = ant_deps.pheromone_cache.get("bug:mod.func_a")
    assert stored is not None
    assert isinstance(stored, BugPheromone)
    assert stored.function_name == "mod.func_a"


@pytest.mark.asyncio
async def test_report_bug_skips_below_threshold(
    ant_deps: AntDeps,
) -> None:
    """report_bug must NOT deposit a pheromone when confidence < min_confidence."""
    from bichos.agents.ant.tools import report_bug

    ctx = _make_ctx(ant_deps)
    # Below min_confidence threshold (0.7).
    result = await report_bug(
        ctx, "mod.func_b", "Possible issue", severity=4, confidence=0.3
    )

    assert (
        "below" in result.lower()
        or "threshold" in result.lower()
        or "logged" in result.lower()
    )
    stored = ant_deps.pheromone_cache.get("bug:mod.func_b")
    assert stored is None


@pytest.mark.asyncio
async def test_report_bug_skips_low_severity(
    ant_deps: AntDeps,
) -> None:
    """report_bug must NOT deposit when severity < 3, even if confidence is high."""
    from bichos.agents.ant.tools import report_bug

    ctx = _make_ctx(ant_deps)
    result = await report_bug(
        ctx, "mod.func_a", "Trivial style issue", severity=2, confidence=0.95
    )

    assert (
        "below" in result.lower()
        or "threshold" in result.lower()
        or "logged" in result.lower()
    )
    stored = ant_deps.pheromone_cache.get("bug:mod.func_a")
    assert stored is None


# ---------------------------------------------------------------------------
# get_pheromone_trail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_pheromone_trail_returns_matching_pheromones(
    ant_deps: AntDeps,
) -> None:
    """get_pheromone_trail returns pheromones whose function_name starts with module."""
    # Deposit two pheromones in the same module and one in a different module.
    for fn in ("mod.func_a", "mod.func_b"):
        ant_deps.pheromone_cache.deposit(
            BugPheromone(
                key=f"bug:{fn}",
                depositor="ant-seed",
                severity=3,
                file_path="mod.py",
                function_name=fn,
                description="seed",
                intensity=10.0,
                confidence=0.8,
            )
        )
    # Different module.
    ant_deps.pheromone_cache.deposit(
        BugPheromone(
            key="bug:other.func_x",
            depositor="ant-seed",
            severity=2,
            file_path="other.py",
            function_name="other.func_x",
            description="other module",
            intensity=5.0,
            confidence=0.8,
        )
    )

    from bichos.agents.ant.tools import get_pheromone_trail

    ctx = _make_ctx(ant_deps)
    trail = await get_pheromone_trail(ctx, "mod")

    assert isinstance(trail, list)
    assert len(trail) == 2
    for entry in trail:
        assert isinstance(entry, dict)
        assert entry["function_name"].startswith("mod")


@pytest.mark.asyncio
async def test_get_pheromone_trail_empty_when_no_match(
    ant_deps: AntDeps,
) -> None:
    """get_pheromone_trail returns an empty list when no pheromones match the module."""
    from bichos.agents.ant.tools import get_pheromone_trail

    ctx = _make_ctx(ant_deps)
    trail = await get_pheromone_trail(ctx, "nonexistent_module")
    assert trail == []
