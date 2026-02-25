"""bichos CLI — entry point for the swarm QA framework."""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from loguru import logger

from bichos import __version__
from bichos.config import HiveConfig
from bichos.logging import configure_logging

app = typer.Typer(
    name="bichos",
    help="Bio-Mimetic Swarm Intelligence Framework for Software QA",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"bichos {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: B008
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    json_logs: bool = typer.Option(False, "--json-logs", help="Emit logs as JSON."),  # noqa: B008
    log_level: str = typer.Option("INFO", "--log-level", help="Log level."),  # noqa: B008
) -> None:
    """bichos — Bio-Mimetic Swarm Intelligence for Software QA."""
    configure_logging(level=log_level, json=json_logs)


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to the repository to analyse."),  # noqa: B008
    ants: int = typer.Option(5, "--ants", "-n", help="Number of ant forager agents."),  # noqa: B008
    model: str = typer.Option(  # noqa: B008
        "openai:gpt-4o", "--model", "-m", help="PydanticAI model string."
    ),
    min_confidence: float = typer.Option(  # noqa: B008
        0.7, "--min-confidence", help="Minimum bug confidence threshold."
    ),
    output: Path | None = typer.Option(  # noqa: B008
        None, "--output", "-o", help="Write report to file."
    ),
) -> None:
    """Analyse a repository using an ant swarm."""
    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        raise typer.Exit(code=1)

    config = HiveConfig(
        ant_count=ants,
        ant_model=model,
        min_confidence=min_confidence,
    )

    logger.info(f"Starting bichos analysis of {path} with {config.ant_count} ants")
    typer.echo(
        f"[bichos] Analysing {path} — {config.ant_count} ants, model={config.ant_model}"
    )

    # TODO(Phase 5): Wire up Hive Orchestrator
    typer.echo("[bichos] Orchestrator not yet implemented — coming in Phase 5.")
    sys.exit(0)
