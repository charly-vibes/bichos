"""CodeGraph — NetworkX wrapper with typed node metadata."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import networkx as nx


@dataclass
class NodeMeta:
    """Metadata attached to each node in the code graph."""

    name: str
    qualified_name: str
    file_path: str
    lineno: int
    loc: int
    complexity: int
    is_class: bool = False


@dataclass
class CodeGraph:
    """Thin wrapper around a NetworkX DiGraph of code entities."""

    graph: nx.DiGraph
    root: Path
    _meta_cache: dict[str, NodeMeta] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._meta_cache = {
            n: data["meta"] for n, data in self.graph.nodes(data=True) if "meta" in data
        }

    # ── Queries ───────────────────────────────────────────────────────────

    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    def edge_count(self) -> int:
        return self.graph.number_of_edges()

    def meta(self, qname: str) -> NodeMeta | None:
        return self._meta_cache.get(qname)

    def neighbors(self, qname: str) -> list[str]:
        """Return direct callees of *qname*."""
        return list(self.graph.successors(qname))

    def callers(self, qname: str) -> list[str]:
        """Return nodes that call *qname*."""
        return list(self.graph.predecessors(qname))

    def nodes_by_complexity(self, top_n: int = 20) -> list[tuple[str, int]]:
        """Return the top-N nodes by cyclomatic complexity (descending)."""
        scored = [(qname, meta.complexity) for qname, meta in self._meta_cache.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def nodes_in_file(self, rel_path: str) -> list[str]:
        return [
            qname
            for qname, meta in self._meta_cache.items()
            if meta.file_path == rel_path
        ]

    def all_nodes(self) -> Iterator[tuple[str, NodeMeta]]:
        yield from self._meta_cache.items()

    # ── Graph algorithms ──────────────────────────────────────────────────

    def cycles(self) -> list[list[str]]:
        """Return all simple cycles (circular dependencies)."""
        return list(nx.simple_cycles(self.graph))

    def critical_nodes(self, top_n: int = 10) -> list[tuple[str, float]]:
        """Return nodes ranked by betweenness centrality."""
        centrality = nx.betweenness_centrality(self.graph)
        ranked = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_n]

    def heuristic_for(self, qname: str) -> float:
        """Compute the ACO heuristic η for a node.

        η = complexity / max(1, loc)  — high complexity relative to size
        is more interesting for an ant forager to investigate.
        """
        meta = self._meta_cache.get(qname)
        if meta is None:
            return 1.0
        return meta.complexity / max(1, meta.loc)
