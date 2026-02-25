"""bichos CLI — entry point for the swarm QA framework."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from bichos import __version__
from bichos.config import HiveConfig
from bichos.hive.models import AnalysisReport
from bichos.hive.orchestrator import run_hive
from bichos.logging import configure_logging
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import BugPheromone, PheromoneType

app = typer.Typer(
    name="bichos",
    help="Bio-Mimetic Swarm Intelligence Framework for Software QA",
    add_completion=False,
)

console = Console()


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
    json_logs: bool = typer.Option(  # noqa: B008
        False, "--json-logs", help="Emit logs as JSON."
    ),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level."),  # noqa: B008
) -> None:
    """bichos — Bio-Mimetic Swarm Intelligence for Software QA."""
    configure_logging(level=log_level, json=json_logs)


def _print_analysis_table(report: AnalysisReport) -> None:
    """Print a rich table of bug findings plus summary stats."""
    table = Table(title="bichos Analysis Report", show_lines=True)
    table.add_column("Bug", style="bold red")
    table.add_column("File", style="cyan")
    table.add_column("Line", style="yellow", justify="right")
    table.add_column("Severity", style="magenta", justify="right")
    table.add_column("Confidence", style="green", justify="right")

    for bug in report.bugs:
        table.add_row(
            bug.function_name,
            bug.file_path,
            str(bug.line_number),
            str(bug.severity),
            f"{bug.confidence:.2f}",
        )

    console.print(table)

    stats = report.summary_stats
    console.print(
        f"\n[bold]Summary:[/bold] "
        f"{stats.unique_bugs} unique bug(s) found, "
        f"{stats.total_functions_visited} function(s) visited, "
        f"avg confidence {stats.avg_confidence:.2f}"
    )


@app.command()
def analyze(
    path: Path = typer.Argument(  # noqa: B008
        ..., help="Path to the repository to analyse."
    ),
    output: str = typer.Option(  # noqa: B008
        "table", "--output", help="Output format: table or json."
    ),
    config: Path | None = typer.Option(  # noqa: B008
        None, "--config", help="JSON file with HiveConfig."
    ),
    agents: int | None = typer.Option(  # noqa: B008
        None, "--agents", "-n", help="Number of ant agents (overrides config)."
    ),
    seed: int | None = typer.Option(  # noqa: B008
        None, "--seed", help="Random seed for deterministic mode."
    ),
) -> None:
    """Analyse a repository using an ant swarm."""
    if not path.exists():
        typer.echo(f"Error: path does not exist: {path}", err=True)
        raise typer.Exit(code=1)

    # Load config
    try:
        if config is not None:
            hive_config = HiveConfig.model_validate_json(config.read_text())
        else:
            hive_config = HiveConfig.default()
    except Exception as e:
        typer.echo(f"Error loading config: {e}", err=True)
        raise typer.Exit(code=1) from e

    # Apply overrides (use model_validate to re-run field constraints)
    if agents is not None:
        data = hive_config.model_dump()
        data["ant_count"] = agents
        try:
            hive_config = HiveConfig.model_validate(data)
        except Exception as e:
            typer.echo(f"Error: invalid --agents value: {e}", err=True)
            raise typer.Exit(code=1) from e

    if seed is not None:
        logger.debug(f"Deterministic mode: seed={seed}")

    logger.info(f"Starting bichos analysis of {path} with {hive_config.ant_count} ants")

    try:
        report: AnalysisReport = asyncio.run(run_hive(path, hive_config))
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

    if output == "json":
        typer.echo(report.model_dump_json(indent=2))
    else:
        _print_analysis_table(report)


@app.command()
def stats(
    cache_dir: Path = typer.Argument(  # noqa: B008
        ..., help="Directory of the pheromone cache."
    ),
) -> None:
    """Print a pheromone intensity heatmap from a cache directory."""
    cache = PheromoneCache(cache_dir=cache_dir, rho=0.1)

    pheromones: list[BugPheromone] = []
    for entry in cache.iter_by_type(PheromoneType.BUG):
        if isinstance(entry, BugPheromone):
            pheromones.append(entry)

    if not pheromones:
        typer.echo("No pheromones found.")
        return

    # Sort by intensity descending, take top 20
    pheromones.sort(key=lambda p: p.intensity, reverse=True)
    top = pheromones[:20]

    table = Table(title="Pheromone Heatmap (Top 20)", show_lines=True)
    table.add_column("Function", style="cyan")
    table.add_column("Intensity", style="magenta", justify="right")

    for p in top:
        table.add_row(p.function_name, f"{p.intensity:.2f}")

    console.print(table)
