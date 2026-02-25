"""AST-based code graph builder for bichos."""

from __future__ import annotations

import ast
from pathlib import Path

import networkx as nx
from radon.complexity import cc_visit

from bichos.graph.models import CodeGraph, NodeMeta


def _extract_calls(tree: ast.AST) -> list[str]:
    """Return a flat list of function names called anywhere in tree."""
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    return calls


def _complexity_for(source: str, name: str) -> int:
    """Return the cyclomatic complexity of a named function/class in source."""
    try:
        results = cc_visit(source)
        for block in results:
            if block.name == name:
                return block.complexity
    except Exception:
        pass
    return 1


def build_code_graph(root: Path, max_files: int = 500) -> CodeGraph:
    """Parse all Python files under *root* and build a directed call graph.

    Nodes represent functions and classes. Edges represent static call
    relationships inferred from AST analysis.

    Args:
        root:      Repository root directory.
        max_files: Maximum number of .py files to process.

    Returns:
        A :class:`CodeGraph` wrapping a NetworkX DiGraph.
    """
    graph: nx.DiGraph = nx.DiGraph()
    py_files = sorted(root.rglob("*.py"))[:max_files]

    # First pass: register all function/class nodes
    node_sources: dict[str, str] = {}  # qualified_name → source text of function

    for filepath in py_files:
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            continue

        rel_path = str(filepath.relative_to(root))
        module_name = rel_path.replace("/", ".").removesuffix(".py")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                qname = f"{module_name}.{node.name}"
                loc = (node.end_lineno or node.lineno) - node.lineno + 1
                complexity = _complexity_for(source, node.name)

                meta = NodeMeta(
                    name=node.name,
                    qualified_name=qname,
                    file_path=rel_path,
                    lineno=node.lineno,
                    loc=loc,
                    complexity=complexity,
                    is_class=isinstance(node, ast.ClassDef),
                )
                graph.add_node(qname, meta=meta)
                node_sources[qname] = ast.get_source_segment(source, node) or ""

    # Second pass: add call edges
    for filepath in py_files:
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(filepath))
        except SyntaxError:
            continue

        rel_path = str(filepath.relative_to(root))
        module_name = rel_path.replace("/", ".").removesuffix(".py")

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            caller = f"{module_name}.{node.name}"
            if caller not in graph:
                continue

            for call_name in _extract_calls(node):
                # Resolve: look for any node whose simple name matches
                for candidate in graph.nodes:
                    if candidate.endswith(f".{call_name}"):
                        if not graph.has_edge(caller, candidate):
                            graph.add_edge(caller, candidate, call_count=1)
                        else:
                            graph[caller][candidate]["call_count"] += 1
                        break  # only add one edge per call site

    return CodeGraph(graph=graph, root=root)
