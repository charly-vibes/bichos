"""Tests for the bichos CLI — analyze and stats commands."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from bichos.agents.ant.models import BugReport
from bichos.cli import app
from bichos.config import HiveConfig
from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats
from bichos.stigmergy.models import BugPheromone, PheromoneType

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_bug_report(**kwargs: object) -> BugReport:
    defaults: dict[str, object] = {
        "function_name": "foo",
        "file_path": "src/foo.py",
        "line_number": 42,
        "description": "null pointer dereference",
        "severity": 7,
        "confidence": 0.9,
    }
    defaults.update(kwargs)
    return BugReport.model_validate(defaults)


def _make_analysis_report(bugs: list[BugReport] | None = None) -> AnalysisReport:
    if bugs is None:
        bugs = [_make_bug_report()]
    return AnalysisReport(
        bugs=bugs,
        summary_stats=SummaryStats(
            total_functions_visited=10,
            total_bugs_found=len(bugs),
            unique_bugs=len(bugs),
            avg_confidence=0.85,
        ),
        pheromone_heatmap={"foo": 42.5},
        metadata=ReportMetadata(
            repo_path="/tmp/testrepo",
            agent_count=3,
            timestamp="2026-02-25T00:00:00+00:00",
            total_tokens=1000,
        ),
    )


def _make_bug_pheromone(function_name: str, intensity: float) -> BugPheromone:
    return BugPheromone(
        key=f"bug:src/foo.py:{function_name}",
        pheromone_type=PheromoneType.BUG,
        intensity=intensity,
        depositor="ant-0",
        severity=3,
        file_path="src/foo.py",
        function_name=function_name,
        description="test bug",
        confidence=0.8,
    )


# ---------------------------------------------------------------------------
# --version flag
# ---------------------------------------------------------------------------


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "bichos" in result.output


# ---------------------------------------------------------------------------
# analyze command — table output (default)
# ---------------------------------------------------------------------------


def test_analyze_table_output(tmp_path: Path) -> None:
    report = _make_analysis_report()

    with patch("bichos.cli.run_hive", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["analyze", str(tmp_path)])

    assert result.exit_code == 0
    # rich table should contain the column headers
    assert "File" in result.output
    assert "Line" in result.output
    assert "Severity" in result.output
    assert "Confidence" in result.output
    # bug data present
    assert "src/foo.py" in result.output


# ---------------------------------------------------------------------------
# analyze command — JSON output
# ---------------------------------------------------------------------------


def test_analyze_json_output(tmp_path: Path) -> None:
    report = _make_analysis_report()

    with patch("bichos.cli.run_hive", new=AsyncMock(return_value=report)):
        result = runner.invoke(app, ["analyze", str(tmp_path), "--output", "json"])

    assert result.exit_code == 0
    # Strip any loguru log lines (which may be mixed into output) before the JSON
    output = result.output
    json_start = output.find("{")
    assert json_start != -1, f"No JSON found in output: {output!r}"
    parsed = json.loads(output[json_start:])
    assert "bugs" in parsed
    assert "summary_stats" in parsed
    assert len(parsed["bugs"]) == 1
    assert parsed["bugs"][0]["function_name"] == "foo"


# ---------------------------------------------------------------------------
# analyze command — --config flag
# ---------------------------------------------------------------------------


def test_analyze_config_file(tmp_path: Path) -> None:
    report = _make_analysis_report()
    config_data = {"ant_count": 7}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    captured_configs: list[HiveConfig] = []

    async def _mock_run_hive(repo_path: Path, config: HiveConfig) -> AnalysisReport:
        captured_configs.append(config)
        return report

    with patch("bichos.cli.run_hive", new=_mock_run_hive):
        result = runner.invoke(
            app, ["analyze", str(tmp_path), "--config", str(config_file)]
        )

    assert result.exit_code == 0
    assert len(captured_configs) == 1
    assert captured_configs[0].ant_count == 7


# ---------------------------------------------------------------------------
# analyze command — --agents flag overrides config
# ---------------------------------------------------------------------------


def test_analyze_agents_override(tmp_path: Path) -> None:
    report = _make_analysis_report()

    captured_configs: list[HiveConfig] = []

    async def _mock_run_hive(repo_path: Path, config: HiveConfig) -> AnalysisReport:
        captured_configs.append(config)
        return report

    with patch("bichos.cli.run_hive", new=_mock_run_hive):
        result = runner.invoke(app, ["analyze", str(tmp_path), "--agents", "3"])

    assert result.exit_code == 0
    assert len(captured_configs) == 1
    assert captured_configs[0].ant_count == 3


# ---------------------------------------------------------------------------
# analyze command — error: non-existent repo_path
# ---------------------------------------------------------------------------


def test_analyze_path_not_found() -> None:
    result = runner.invoke(app, ["analyze", "/nonexistent/path/that/does/not/exist"])
    assert result.exit_code == 1
    # Error message should appear (in stderr or stdout)
    combined = result.output
    assert "not exist" in combined.lower() or "error" in combined.lower()


# ---------------------------------------------------------------------------
# analyze command — error: invalid --config file
# ---------------------------------------------------------------------------


def test_analyze_invalid_config_file(tmp_path: Path) -> None:
    bad_config = tmp_path / "bad.json"
    bad_config.write_text("{ this is not valid json }")

    result = runner.invoke(app, ["analyze", str(tmp_path), "--config", str(bad_config)])
    assert result.exit_code == 1
    combined = result.output
    assert "error" in combined.lower()


# ---------------------------------------------------------------------------
# analyze command — error: invalid --agents value
# ---------------------------------------------------------------------------


def test_analyze_agents_invalid(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", str(tmp_path), "--agents", "0"])
    assert result.exit_code == 1
    assert "error" in result.output.lower()


# ---------------------------------------------------------------------------
# stats command — top-20 pheromones
# ---------------------------------------------------------------------------


def test_stats_top20(tmp_path: Path) -> None:
    pheromones = [_make_bug_pheromone(f"func_{i}", float(i * 2)) for i in range(25)]

    mock_cache = MagicMock()
    mock_cache.iter_by_type.return_value = iter(pheromones)

    with patch("bichos.cli.PheromoneCache", return_value=mock_cache):
        result = runner.invoke(app, ["stats", str(tmp_path)])

    assert result.exit_code == 0
    mock_cache.iter_by_type.assert_called_once_with(PheromoneType.BUG)
    # Should show top 20 by intensity (highest first)
    # func_24 has intensity 48.0, func_23 has 46.0, etc.
    assert "func_24" in result.output
    assert "func_23" in result.output
    # func_4 has intensity 8.0, func_3 has 6.0 — these are outside top 20
    # top 20 = indices 5..24
    assert "func_4" not in result.output


# ---------------------------------------------------------------------------
# stats command — empty cache
# ---------------------------------------------------------------------------


def test_stats_empty_cache(tmp_path: Path) -> None:
    mock_cache = MagicMock()
    mock_cache.iter_by_type.return_value = iter([])

    with patch("bichos.cli.PheromoneCache", return_value=mock_cache):
        result = runner.invoke(app, ["stats", str(tmp_path)])

    assert result.exit_code == 0
    assert "no pheromones" in result.output.lower()


# ---------------------------------------------------------------------------
# benchmark command
# ---------------------------------------------------------------------------


def _make_empty_report() -> AnalysisReport:
    """Return a valid AnalysisReport with no bugs (suitable for mock responses)."""
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
            repo_path="/tmp/testrepo",
            agent_count=1,
            timestamp="2026-02-25T00:00:00+00:00",
            total_tokens=0,
        ),
    )


def test_benchmark_default_runs() -> None:
    """benchmark with default args mocks run_hive and exits 0."""
    mock_report = _make_empty_report()
    mock_run_hive = AsyncMock(return_value=mock_report)

    with patch("bichos.cli.run_hive", new=mock_run_hive):
        result = runner.invoke(app, ["benchmark", "--skip-slow"])

    assert result.exit_code == 0, result.output


def test_benchmark_skip_slow_uses_mock() -> None:
    """--skip-slow flag means run_hive is NOT called with real invocation."""
    mock_run_hive = AsyncMock(return_value=_make_empty_report())

    with patch("bichos.cli.run_hive", new=mock_run_hive):
        result = runner.invoke(app, ["benchmark", "--skip-slow"])

    assert result.exit_code == 0, result.output
    # With --skip-slow, the mock run_hive should not have been called
    mock_run_hive.assert_not_called()


def test_benchmark_dataset_simple() -> None:
    """--dataset simple routes only simple_bugs paths through _compute_metrics.

    Patches _compute_metrics (always called even in --skip-slow mode) so routing
    is verified without needing a real API key or live run_hive call.
    """
    import bichos.cli as cli_module

    captured_paths: list[Path] = []
    original_compute = cli_module._compute_metrics

    def _capturing_compute(
        report: AnalysisReport, fixture_path: Path, ground_truth_count: int
    ) -> dict[str, float]:
        captured_paths.append(fixture_path)
        return original_compute(report, fixture_path, ground_truth_count)

    with patch("bichos.cli._compute_metrics", side_effect=_capturing_compute):
        result = runner.invoke(
            app,
            ["benchmark", "--skip-slow", "--dataset", "simple", "--seeds", "1"],
        )

    assert result.exit_code == 0, result.output
    assert len(captured_paths) > 0, "No paths captured — routing not exercised"
    for p in captured_paths:
        assert "simple_bugs" in str(p), f"Expected simple_bugs path, got {p}"
    assert "medium_bugs" not in " ".join(str(p) for p in captured_paths)


def test_benchmark_dataset_medium() -> None:
    """--dataset medium routes only medium_bugs paths through _compute_metrics.

    Patches _compute_metrics (always called even in --skip-slow mode) so routing
    is verified without needing a real API key or live run_hive call.
    """
    import bichos.cli as cli_module

    captured_paths: list[Path] = []
    original_compute = cli_module._compute_metrics

    def _capturing_compute(
        report: AnalysisReport, fixture_path: Path, ground_truth_count: int
    ) -> dict[str, float]:
        captured_paths.append(fixture_path)
        return original_compute(report, fixture_path, ground_truth_count)

    with patch("bichos.cli._compute_metrics", side_effect=_capturing_compute):
        result = runner.invoke(
            app,
            ["benchmark", "--skip-slow", "--dataset", "medium", "--seeds", "1"],
        )

    assert result.exit_code == 0, result.output
    assert len(captured_paths) > 0, "No paths captured — routing not exercised"
    for p in captured_paths:
        assert "medium_bugs" in str(p), f"Expected medium_bugs path, got {p}"
    assert "simple_bugs" not in " ".join(str(p) for p in captured_paths)


def test_benchmark_single_mode() -> None:
    """--modes aco results in only aco mode appearing in output JSON."""
    mock_report = _make_empty_report()
    mock_run_hive = AsyncMock(return_value=mock_report)

    with (
        patch("bichos.cli.run_hive", new=mock_run_hive),
        patch("bichos.cli._FIXTURES_ROOT", Path("/nonexistent")),
    ):
        result = runner.invoke(
            app,
            ["benchmark", "--skip-slow", "--modes", "aco"],
        )

    assert result.exit_code == 0, result.output
    # The output should mention aco but not complexity or random
    assert "aco" in result.output
    assert "complexity" not in result.output
    assert "random" not in result.output


def test_benchmark_output_file(tmp_path: Path) -> None:
    """--output-file creates the file at the specified path."""
    output_file = tmp_path / "results.json"
    mock_run_hive = AsyncMock(return_value=_make_empty_report())

    with patch("bichos.cli.run_hive", new=mock_run_hive):
        result = runner.invoke(
            app,
            ["benchmark", "--skip-slow", "--output-file", str(output_file)],
        )

    assert result.exit_code == 0, result.output
    assert output_file.exists(), "Output file was not created"


def test_benchmark_output_json_structure(tmp_path: Path) -> None:
    """Output JSON has required keys: dataset, modes, and per-mode stats."""
    output_file = tmp_path / "bench.json"
    mock_run_hive = AsyncMock(return_value=_make_empty_report())

    with patch("bichos.cli.run_hive", new=mock_run_hive):
        result = runner.invoke(
            app,
            [
                "benchmark",
                "--skip-slow",
                "--modes",
                "aco",
                "--seeds",
                "1",
                "--output-file",
                str(output_file),
            ],
        )

    assert result.exit_code == 0, result.output
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert "dataset" in data, f"Missing 'dataset' key: {data}"
    assert "modes" in data, f"Missing 'modes' key: {data}"
    assert "aco" in data["modes"], f"Missing 'aco' in modes: {data['modes']}"
    mode_data = data["modes"]["aco"]
    assert "seeds" in mode_data
    assert "mean_bugs" in mode_data
    assert "mean_precision" in mode_data
    assert "mean_recall" in mode_data


def test_benchmark_invalid_dataset() -> None:
    """--dataset with an unknown value causes exit code 1."""
    result = runner.invoke(app, ["benchmark", "--dataset", "badname"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# analyze command — invalid --agents value (negative int fails HiveConfig)
# ---------------------------------------------------------------------------


def test_analyze_invalid_agents_value(tmp_path: Path) -> None:
    """--agents=-1 triggers HiveConfig validation error, exit code 1."""
    result = runner.invoke(app, ["analyze", str(tmp_path), "--agents", "-1"])
    assert result.exit_code == 1
    assert "Error: invalid --agents value" in result.output


# ---------------------------------------------------------------------------
# benchmark command — invalid mode name
# ---------------------------------------------------------------------------


def test_benchmark_invalid_mode() -> None:
    """--modes invalid_mode causes exit code 1 with error message."""
    result = runner.invoke(app, ["benchmark", "--modes", "invalid_mode"])
    assert result.exit_code == 1
    assert "Error: invalid mode(s)" in result.output


# ---------------------------------------------------------------------------
# benchmark command — no API key warning
# ---------------------------------------------------------------------------


def test_benchmark_no_api_key_warning() -> None:
    """When no API key is set and --skip-slow is NOT passed, a warning is printed."""
    result = runner.invoke(
        app,
        ["benchmark"],
        env={"ANTHROPIC_API_KEY": "", "OPENAI_API_KEY": ""},
    )
    assert "No ANTHROPIC_API_KEY" in result.output


# ---------------------------------------------------------------------------
# benchmark command — run_hive exception falls back to mock report
# ---------------------------------------------------------------------------


def test_benchmark_run_hive_exception() -> None:
    """When run_hive raises RuntimeError, benchmark catches it and uses mock report."""
    with (
        patch(
            "bichos.cli.run_hive",
            new=MagicMock(side_effect=RuntimeError("boom")),
        ),
    ):
        result = runner.invoke(
            app,
            ["benchmark", "--seeds", "1", "--modes", "aco"],
            env={"ANTHROPIC_API_KEY": "sk-fake-key", "OPENAI_API_KEY": ""},
        )
    assert result.exit_code == 0, result.output
