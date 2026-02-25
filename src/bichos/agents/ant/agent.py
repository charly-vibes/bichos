"""PydanticAI forager agent for the Ant caste."""

from __future__ import annotations

from pydantic_ai import Agent

from bichos.agents.ant.models import AntDeps, ExplorationResult

# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------
# Model is intentionally omitted here; it is supplied at runtime inside
# run_ant() so each call can use the model string stored in HiveConfig.
# Tools (choose_next_function, analyze_code, report_bug) are registered
# externally in agents/ant/tools.py — see that module for implementations.
# ---------------------------------------------------------------------------

forager: Agent[AntDeps, ExplorationResult] = Agent(
    # model omitted — provided per-run via run_ant()
    deps_type=AntDeps,
    output_type=ExplorationResult,
    retries=1,
    system_prompt=(
        "You are a forager ant exploring a Python codebase to find bugs. "
        "Your task is to navigate through the call graph and inspect code "
        "for defects.\n\n"
        "Workflow:\n"
        "1. Use `choose_next_function` to decide which function to visit next, "
        "guided by pheromone trails and the heuristic edge weights.\n"
        "2. Use `analyze_code` to read and assess the source of each "
        "function you visit.\n"
        "3. If you discover a bug, use `report_bug` to deposit a pheromone trail and "
        "record the finding.\n"
        "4. You MUST visit at least 5 distinct functions before concluding.\n"
        "5. Return a structured ExplorationResult containing the ordered path you "
        "visited, all bug reports emitted, and the total token count consumed."
    ),
)

# tools registered in tools.py


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


async def run_ant(
    deps: AntDeps,
    start_function: str | None = None,
) -> ExplorationResult:
    """Run a single forager ant exploration.

    Args:
        deps: Dependency bundle containing the pheromone cache, code graph,
            configuration, RNG, and LLM semaphore.
        start_function: Optional qualified function name to begin exploration
            from.  When provided it is passed to the agent as the initial
            user message so the model can orient itself immediately.

    Returns:
        An ExplorationResult summarising visited functions and bugs found.
    """
    async with deps.llm_semaphore:
        user_prompt: str = (
            f"Start exploration at function: {start_function}"
            if start_function is not None
            else "Begin exploration from the highest-pheromone entry point."
        )

        result = await forager.run(
            user_prompt,
            deps=deps,
            model=deps.config.ant_model,
        )

    return result.output
