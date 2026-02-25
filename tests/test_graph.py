"""Tests for the code graph builder."""

from __future__ import annotations

from pathlib import Path

import pytest

from bichos.graph.builder import build_code_graph
from bichos.graph.models import CodeGraph


@pytest.fixture()
def simple_graph(simple_bugs_path: Path) -> CodeGraph:
    return build_code_graph(simple_bugs_path)


# ── Basic graph properties ────────────────────────────────────────────────────


def test_graph_has_nodes(simple_graph: CodeGraph) -> None:
    assert simple_graph.node_count() > 0


def test_graph_finds_functions(simple_graph: CodeGraph) -> None:
    names = {meta.name for _, meta in simple_graph.all_nodes()}
    assert "divide" in names
    assert "add" in names


def test_graph_finds_classes(simple_graph: CodeGraph) -> None:
    names = {meta.name for _, meta in simple_graph.all_nodes()}
    assert "UserStore" in names
    assert "EventBus" in names


def test_nodes_have_file_path(simple_graph: CodeGraph) -> None:
    for _, meta in simple_graph.all_nodes():
        assert meta.file_path != ""
        assert meta.file_path.endswith(".py")


def test_nodes_have_positive_loc(simple_graph: CodeGraph) -> None:
    for _, meta in simple_graph.all_nodes():
        assert meta.loc > 0


def test_nodes_have_complexity(simple_graph: CodeGraph) -> None:
    for _, meta in simple_graph.all_nodes():
        assert meta.complexity >= 1


# ── nodes_by_complexity ───────────────────────────────────────────────────────


def test_nodes_by_complexity_ordering(simple_graph: CodeGraph) -> None:
    ranked = simple_graph.nodes_by_complexity(top_n=10)
    complexities = [c for _, c in ranked]
    assert complexities == sorted(complexities, reverse=True)


# ── nodes_in_file ──────────────────────────────────────────────────────────────


def test_nodes_in_file_returns_subset(simple_graph: CodeGraph) -> None:
    # Find a known file path
    file_paths = {meta.file_path for _, meta in simple_graph.all_nodes()}
    some_file = next(iter(file_paths))
    nodes = simple_graph.nodes_in_file(some_file)
    assert len(nodes) > 0
    for qname in nodes:
        meta = simple_graph.meta(qname)
        assert meta is not None
        assert meta.file_path == some_file


# ── heuristic_for ─────────────────────────────────────────────────────────────


def test_heuristic_positive(simple_graph: CodeGraph) -> None:
    for qname, _ in simple_graph.all_nodes():
        h = simple_graph.heuristic_for(qname)
        assert h > 0.0


def test_heuristic_missing_node(simple_graph: CodeGraph) -> None:
    assert simple_graph.heuristic_for("nonexistent.node") == 1.0


# ── max_files cap ─────────────────────────────────────────────────────────────


def test_max_files_limits_graph(simple_bugs_path: Path) -> None:
    g1 = build_code_graph(simple_bugs_path, max_files=1)
    g_all = build_code_graph(simple_bugs_path)
    assert g1.node_count() <= g_all.node_count()


# ── syntax error resilience ───────────────────────────────────────────────────


def test_skips_syntax_errors(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text("def broken(\n    pass\n", encoding="utf-8")
    (tmp_path / "good.py").write_text("def ok(): pass\n", encoding="utf-8")
    g = build_code_graph(tmp_path)
    names = {meta.name for _, meta in g.all_nodes()}
    assert "ok" in names
    # bad.py was skipped — no crash
