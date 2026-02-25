"""Dataclasses and Pydantic models for the Ant Forager agent."""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass

from pydantic import BaseModel, Field

from bichos.config import HiveConfig
from bichos.graph.models import CodeGraph
from bichos.stigmergy.cache import PheromoneCache


@dataclass
class AntDeps:
    """Dependency bundle injected into an Ant Forager agent run.

    Attributes:
        pheromone_cache: Shared persistent pheromone grid.
        code_graph:      Static call-graph of the analysed codebase.
        config:          Top-level hive configuration.
        rng:             Seeded random-number generator for reproducibility.
        llm_semaphore:   Concurrency limit for simultaneous LLM calls.
    """

    pheromone_cache: PheromoneCache
    code_graph: CodeGraph
    config: HiveConfig
    rng: random.Random
    llm_semaphore: asyncio.Semaphore


class BugReport(BaseModel):
    """A single bug finding produced by an Ant Forager agent.

    Attributes:
        function_name: Simple name of the function where the bug was found.
        file_path:     Relative path to the source file.
        line_number:   Line number of the defect.
        description:   Human-readable explanation of the issue.
        severity:      Integer severity on a 1–10 scale (10 = most severe).
        confidence:    Model confidence in the finding, in [0.0, 1.0].
    """

    function_name: str
    file_path: str
    line_number: int
    description: str
    severity: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)


class ExplorationResult(BaseModel):
    """Summary of a single ant forager exploration run.

    Attributes:
        path_visited: Ordered list of qualified function names visited.
        bugs_found:   Bug reports emitted during the exploration.
        tokens_used:  Total LLM tokens consumed (0 if not tracked).
    """

    path_visited: list[str]
    bugs_found: list[BugReport]
    tokens_used: int = 0
