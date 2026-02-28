"""bichos CLI — entry point for the swarm QA framework."""

from __future__ import annotations

import asyncio
import json
import os
import re
import statistics
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from bichos import __version__
from bichos.config import ACOConfig, HiveConfig
from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats
from bichos.hive.orchestrator import run_hive
from bichos.logging import configure_logging
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import BugPheromone, PheromoneType

# Root directory for fixture datasets (resolved relative to this source file)
_FIXTURES_ROOT: Path = Path(__file__).parent.parent.parent / "tests" / "fixtures"

# Valid dataset names
_VALID_DATASETS = frozenset(["simple", "medium", "all"])

# Valid mode names and their ACO configs
_MODE_ACO_CONFIGS: dict[str, ACOConfig] = {
    "aco": ACOConfig.model_validate({"alpha": 1.0, "beta": 2.0}),
    "complexity": ACOConfig.model_validate({"alpha": 0.0, "beta": 2.0}),
    "random": ACOConfig.model_validate({"alpha": 0.0, "beta": 0.0}),
}

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
    model: str | None = typer.Option(  # noqa: B008
        None, "--model", help="Model in <provider>:<name> format, e.g. openai:gpt-4o."
    ),
    base_url: str | None = typer.Option(  # noqa: B008
        None,
        "--base-url",
        help="Override model base_url, e.g. http://localhost:11434/v1.",
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

    if model is not None or base_url is not None:
        model_updates: dict[str, object] = {}
        if model is not None:
            if ":" not in model:
                typer.echo(
                    f"Error: --model must be in <provider>:<name> format,"
                    f" got {model!r}",
                    err=True,
                )
                raise typer.Exit(code=1)
            provider, name = model.split(":", 1)
            model_updates["provider"] = provider
            model_updates["name"] = name
        if base_url is not None:
            model_updates["base_url"] = base_url
        hive_config = hive_config.model_copy(
            update={"model": hive_config.model.model_copy(update=model_updates)}
        )

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


# ---------------------------------------------------------------------------
# benchmark helpers
# ---------------------------------------------------------------------------


def _parse_manifest_bug_counts() -> dict[str, int]:
    """Parse tests/fixtures/MANIFEST.md and return bug counts per dataset.

    Returns a dict like {"simple_bugs": 4, "medium_bugs": 10}.
    """
    manifest_path = _FIXTURES_ROOT / "MANIFEST.md"
    if not manifest_path.exists():
        return {"simple": 0, "medium": 0}

    text = manifest_path.read_text()
    counts: dict[str, int] = {}

    # Find each dataset section and count table rows (non-header, non-separator rows)
    # Sections are delineated by "## <dataset_name>" headings
    section_pattern = re.compile(r"^## (\w+)", re.MULTILINE)
    table_row_pattern = re.compile(r"^\|[^-]", re.MULTILINE)

    sections = list(section_pattern.finditer(text))
    for idx, match in enumerate(sections):
        section_name = match.group(1)
        start = match.end()
        end = sections[idx + 1].start() if idx + 1 < len(sections) else len(text)
        section_text = text[start:end]

        # Count data rows in the markdown table: rows starting with | that are
        # not the header separator row (which contains only dashes and pipes)
        rows = table_row_pattern.findall(section_text)
        # Subtract 1 for the header row (first row)
        data_rows = max(0, len(rows) - 1)
        counts[section_name] = data_rows

    return counts


def _make_mock_report() -> AnalysisReport:
    """Return an empty AnalysisReport suitable for --skip-slow mode."""
    return AnalysisReport(
        bugs=[],
        summary_stats=SummaryStats(
            total_functions_visited=0,
            total_bugs_found=0,
            unique_bugs=0,
            avg_confidence=0.0,
        ),
        pheromone_heatmap={},
        metadata=ReportMetadata(
            repo_path="mock",
            agent_count=1,
            timestamp="",
            total_tokens=0,
        ),
    )


def _compute_metrics(
    report: AnalysisReport,
    fixture_path: Path,
    ground_truth_count: int,
) -> dict[str, float]:
    """Compute precision and recall for a single run against ground truth.

    A bug report is a true positive if its file_path contains the fixture
    dataset directory name (relaxed match).

    Returns:
        Dict with keys: bugs_found, precision, recall
    """
    dataset_name = fixture_path.name  # e.g. "simple_bugs"
    reported_bugs = len(report.bugs)

    # True positives: reported bugs whose file_path contains the dataset dir name
    true_positives = sum(1 for b in report.bugs if dataset_name in b.file_path)

    precision = true_positives / reported_bugs if reported_bugs > 0 else 0.0
    recall = true_positives / ground_truth_count if ground_truth_count > 0 else 0.0

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    tokens_used = float(report.metadata.total_tokens)

    return {
        "bugs_found": float(reported_bugs),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tokens_used": tokens_used,
    }


# ---------------------------------------------------------------------------
# benchmark command
# ---------------------------------------------------------------------------


@app.command()
def benchmark(
    dataset: str = typer.Option(  # noqa: B008
        "all", "--dataset", help="Dataset: simple, medium, all"
    ),
    modes: list[str] = typer.Option(  # noqa: B008
        ["aco", "complexity", "random"], "--modes", help="Modes to benchmark"
    ),
    seeds: int = typer.Option(3, "--seeds", help="Number of random seeds per mode"),  # noqa: B008
    skip_slow: bool = typer.Option(  # noqa: B008
        False, "--skip-slow", help="Skip actual LLM calls, use mock results"
    ),
    output_file: Path | None = typer.Option(  # noqa: B008
        None, "--output-file", help="Write JSON results to file"
    ),
    model: str | None = typer.Option(  # noqa: B008
        None, "--model", help="Model in <provider>:<name> format, e.g. openai:gpt-4o."
    ),
    base_url: str | None = typer.Option(  # noqa: B008
        None,
        "--base-url",
        help="Override model base_url, e.g. http://0.0.0.0:11435/v1.",
    ),
) -> None:
    """Benchmark the swarm across modes and fixture datasets."""
    # Validate model flag format
    if model is not None and ":" not in model:
        typer.echo(
            f"Error: --model must be in <provider>:<name> format, got {model!r}",
            err=True,
        )
        raise typer.Exit(code=1)

    # Validate dataset
    if dataset not in _VALID_DATASETS:
        typer.echo(
            f"Error: invalid --dataset {dataset!r}. "
            f"Choose from: {', '.join(sorted(_VALID_DATASETS))}",
            err=True,
        )
        raise typer.Exit(code=1)

    # Validate modes
    invalid_modes = [m for m in modes if m not in _MODE_ACO_CONFIGS]
    if invalid_modes:
        typer.echo(
            f"Error: invalid mode(s): {invalid_modes}. "
            f"Choose from: {', '.join(sorted(_MODE_ACO_CONFIGS))}",
            err=True,
        )
        raise typer.Exit(code=1)

    # Determine fixture paths
    fixture_paths: list[Path] = []
    if dataset in ("simple", "all"):
        fixture_paths.append(_FIXTURES_ROOT / "simple_bugs")
    if dataset in ("medium", "all"):
        fixture_paths.append(_FIXTURES_ROOT / "medium_bugs")

    # Load ground truth counts
    bug_counts = _parse_manifest_bug_counts()
    # Map fixture path name → planted bug count
    ground_truth: dict[str, int] = {
        "simple_bugs": bug_counts.get("simple_bugs", 4),
        "medium_bugs": bug_counts.get("medium_bugs", 10),
    }

    # Determine whether to use real LLM calls.
    # A model flag pointing at a local provider (ollama) needs no API key.
    has_api_key = bool(
        os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
    has_local_model = model is not None and model.startswith("ollama:")
    use_mock = skip_slow or (not has_api_key and not has_local_model)

    if not has_api_key and not has_local_model and not skip_slow:
        console.print(
            "[yellow]Warning:[/yellow] No ANTHROPIC_API_KEY, OPENAI_API_KEY, or "
            "OPENROUTER_API_KEY found. "
            "Using mock results. Pass --skip-slow to suppress this warning."
        )

    # Results storage: mode → list of per-seed metrics
    mode_results: dict[str, list[dict[str, float]]] = {m: [] for m in modes}

    # Parse optional --model and --base-url flags into model config dict
    model_data: dict[str, str] = {}
    if model is not None:
        provider, name = model.split(":", 1)
        model_data = {"provider": provider, "name": name}
    if base_url is not None:
        model_data["base_url"] = base_url

    for mode in modes:
        aco_config = _MODE_ACO_CONFIGS[mode]
        config_data: dict[str, object] = {"aco": aco_config.model_dump()}
        if model_data:
            config_data["model"] = model_data
        config = HiveConfig.model_validate(config_data)

        for seed_idx in range(seeds):
            for fixture_path in fixture_paths:
                gt_count = ground_truth.get(fixture_path.name, 0)

                if use_mock:
                    report = _make_mock_report()
                else:
                    try:
                        report = asyncio.run(run_hive(fixture_path, config))
                    except Exception as exc:
                        logger.warning(
                            f"run_hive failed for {fixture_path} mode={mode} "
                            f"seed={seed_idx}: {exc}"
                        )
                        report = _make_mock_report()

                metrics = _compute_metrics(report, fixture_path, gt_count)
                mode_results[mode].append(metrics)

    # Aggregate per mode
    aggregated: dict[str, dict[str, object]] = {}
    for mode, seed_metrics in mode_results.items():
        bugs_list = [m["bugs_found"] for m in seed_metrics]
        prec_list = [m["precision"] for m in seed_metrics]
        rec_list = [m["recall"] for m in seed_metrics]
        f1_list = [m["f1"] for m in seed_metrics]
        tokens_list = [m["tokens_used"] for m in seed_metrics]

        aggregated[mode] = {
            "seeds": seed_metrics,
            "mean_bugs": statistics.mean(bugs_list) if bugs_list else 0.0,
            "std_bugs": statistics.stdev(bugs_list) if len(bugs_list) > 1 else 0.0,
            "mean_precision": statistics.mean(prec_list) if prec_list else 0.0,
            "mean_recall": statistics.mean(rec_list) if rec_list else 0.0,
            "mean_f1": statistics.mean(f1_list) if f1_list else 0.0,
            "std_f1": statistics.stdev(f1_list) if len(f1_list) > 1 else 0.0,
            "mean_tokens": statistics.mean(tokens_list) if tokens_list else 0.0,
            "std_tokens": (
                statistics.stdev(tokens_list) if len(tokens_list) > 1 else 0.0
            ),
        }

    # Build output structure
    output_data: dict[str, object] = {
        "dataset": dataset,
        "modes": aggregated,
    }

    # Write JSON output file if requested
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(output_data, indent=2))
        console.print(f"Results written to [cyan]{output_file}[/cyan]")

    # Print rich summary table
    table = Table(title=f"Benchmark Results (dataset={dataset})", show_lines=True)
    table.add_column("Mode", style="bold cyan")
    table.add_column("Mean Bugs", justify="right")
    table.add_column("Std Bugs", justify="right")
    table.add_column("Mean Precision", justify="right", style="green")
    table.add_column("Mean Recall", justify="right", style="yellow")
    table.add_column("Mean F1", justify="right", style="bold green")
    table.add_column("Mean Tokens", justify="right")

    for mode in modes:
        agg = aggregated[mode]
        table.add_row(
            mode,
            f"{agg['mean_bugs']:.2f}",
            f"{agg['std_bugs']:.2f}",
            f"{agg['mean_precision']:.3f}",
            f"{agg['mean_recall']:.3f}",
            f"{agg['mean_f1']:.3f}",
            f"{agg['mean_tokens']:.1f}",
        )

    console.print(table)
