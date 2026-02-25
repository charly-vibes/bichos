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
