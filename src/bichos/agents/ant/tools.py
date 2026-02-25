"""Forager ant tools — registered on the forager agent from agent.py."""

from __future__ import annotations

from pathlib import Path

from pydantic_ai import RunContext

from bichos.agents.ant.aco import compute_probabilities, stochastic_select
from bichos.agents.ant.agent import forager
from bichos.agents.ant.models import AntDeps
from bichos.stigmergy.models import BugPheromone, PheromoneType

# ---------------------------------------------------------------------------
# Tool: choose_next_function
# ---------------------------------------------------------------------------


@forager.tool
async def choose_next_function(ctx: RunContext[AntDeps], current_function: str) -> str:
    """Navigate to the next function using ACO-weighted pheromone trails.

    Args:
        ctx:              PydanticAI run context carrying AntDeps.
        current_function: Qualified name of the function currently being visited.

    Returns:
        Qualified name of the next function to visit.  Returns *current_function*
        unchanged when there are no outgoing edges (dead-end guard).
    """
    neighbors = ctx.deps.code_graph.neighbors(current_function)
    if not neighbors:
        return current_function

    # Build pheromone intensity map; fall back to 1.0 when no trail exists.
    pheromones: dict[str, float] = {}
    for neighbor in neighbors:
        entry = ctx.deps.pheromone_cache.get(f"bug:{neighbor}")
        pheromones[neighbor] = entry.intensity if entry is not None else 1.0

    heuristics: dict[str, float] = {
        n: ctx.deps.code_graph.heuristic_for(n) for n in neighbors
    }

    probs = compute_probabilities(
        neighbors,
        pheromones,
        heuristics,
        ctx.deps.config.aco.alpha,
        ctx.deps.config.aco.beta,
    )
    return stochastic_select(probs)


# ---------------------------------------------------------------------------
# Tool: analyze_code
# ---------------------------------------------------------------------------


@forager.tool
async def analyze_code(ctx: RunContext[AntDeps], function_name: str) -> str:
    """Return a source-code snippet for the named function.

    Reads the file referenced in the code graph's node metadata and extracts
    the 20 lines either side of the declared line number.

    Args:
        ctx:           PydanticAI run context carrying AntDeps.
        function_name: Qualified name of the function to inspect.

    Returns:
        A formatted string containing location metadata and the source snippet,
        or a descriptive error message if the function or file cannot be found.
    """
    meta = ctx.deps.code_graph.meta(function_name)
    if meta is None:
        return f"Function {function_name!r} not found in code graph."

    source_path = Path(ctx.deps.code_graph.root) / meta.file_path
    try:
        source_lines = source_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return (
            f"{meta.file_path}:{meta.lineno} "
            f"({meta.loc} loc, complexity={meta.complexity})\n\n"
            f"[Source file not found: {source_path}]"
        )

    # Extract lines around lineno (1-indexed), clamped to file bounds.
    window = 20
    start = max(0, meta.lineno - 1 - window)
    end = min(len(source_lines), meta.lineno + window)
    snippet = "\n".join(source_lines[start:end])

    header = (
        f"{meta.file_path}:{meta.lineno} ({meta.loc} loc, complexity={meta.complexity})"
    )
    return f"{header}\n\n{snippet}"


# ---------------------------------------------------------------------------
# Tool: report_bug
# ---------------------------------------------------------------------------


@forager.tool
async def report_bug(
    ctx: RunContext[AntDeps],
    function_name: str,
    description: str,
    severity: int,
    confidence: float,
) -> str:
    """Record a bug finding and, when above threshold, deposit a BugPheromone.

    The pheromone is deposited only when **both** conditions hold:
    - ``confidence >= config.min_confidence``
    - ``severity >= 3``

    Args:
        ctx:           PydanticAI run context carrying AntDeps.
        function_name: Qualified name of the affected function.
        description:   Human-readable description of the defect.
        severity:      Severity on a 1–10 scale (maps to BugPheromone 1–5).
        confidence:    Model confidence in the finding, in [0.0, 1.0].

    Returns:
        A string summarising the outcome.
    """
    above_confidence = confidence >= ctx.deps.config.min_confidence
    above_severity = severity >= 3

    if above_confidence and above_severity:
        meta = ctx.deps.code_graph.meta(function_name)
        file_path = meta.file_path if meta is not None else ""

        # Map severity [1-10] → BugPheromone severity [1-5]
        mapped_severity = min(5, max(1, severity // 2))

        # Intensity is proportional to severity × confidence, clamped to [0, 100]
        raw_intensity = float(severity) * confidence
        intensity = max(0.0, min(100.0, raw_intensity))

        pheromone = BugPheromone(
            key=f"bug:{function_name}",
            depositor="ant",
            severity=mapped_severity,
            file_path=file_path,
            function_name=function_name,
            description=description,
            confidence=confidence,
            intensity=intensity,
        )
        ctx.deps.pheromone_cache.deposit(pheromone)
        return "Bug reported and pheromone deposited."

    return (
        f"Bug logged but below threshold "
        f"(confidence={confidence:.2f}, severity={severity})."
    )


# ---------------------------------------------------------------------------
# Tool: get_pheromone_trail
# ---------------------------------------------------------------------------


@forager.tool
async def get_pheromone_trail(ctx: RunContext[AntDeps], module: str) -> list[dict]:  # type: ignore[type-arg]
    """Return all BugPheromones associated with a given module prefix.

    Iterates over all live bug pheromones in the cache and returns those
    whose ``function_name`` starts with *module* or whose key contains *module*.

    Args:
        ctx:    PydanticAI run context carrying AntDeps.
        module: Module name prefix to filter by (e.g. ``"mypackage.utils"``).

    Returns:
        List of pheromone dicts (``model_dump()`` output) for matching entries.
    """
    matching: list[dict] = []  # type: ignore[type-arg]
    for pheromone in ctx.deps.pheromone_cache.iter_by_type(PheromoneType.BUG):
        if isinstance(pheromone, BugPheromone) and (
            pheromone.function_name.startswith(module) or module in pheromone.key
        ):
            matching.append(pheromone.model_dump())
    return matching
