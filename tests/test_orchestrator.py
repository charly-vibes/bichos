"""Tests for hive orchestrator data models (bichos-46o).

Tests cover:
- SwarmState dataclass fields and defaults
- SummaryStats Pydantic model with ge=0 constraints
- ReportMetadata Pydantic model field constraints
- AnalysisReport Pydantic model with nested models
- pheromone_heatmap intensity values in [0.0, 100.0]
- confidence values in [0.0, 1.0]
- Round-trip serialization of AnalysisReport
"""

from dataclasses import fields
from pathlib import Path

import networkx as nx
import pytest
from pydantic import ValidationError

from bichos.agents.ant.models import BugReport, ExplorationResult
from bichos.config import HiveConfig
from bichos.graph.models import CodeGraph
from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats, SwarmState
from bichos.stigmergy.cache import PheromoneCache

# ── Fixtures ──────────────────────────────────────────────────────────────────


def _make_code_graph() -> CodeGraph:
    return CodeGraph(graph=nx.DiGraph(), root=Path("."))


def _make_pheromone_cache(tmp_path: Path) -> PheromoneCache:
    return PheromoneCache(cache_dir=tmp_path / "test_cache")


def _make_config() -> HiveConfig:
    return HiveConfig.default()


def _make_bug_report() -> BugReport:
    return BugReport(
        function_name="foo",
        file_path="src/foo.py",
        line_number=10,
        description="A bug",
        severity=5,
        confidence=0.9,
    )


def _make_exploration_result() -> ExplorationResult:
    return ExplorationResult(
        path_visited=["foo", "bar"],
        bugs_found=[_make_bug_report()],
        tokens_used=100,
    )


# ── SwarmState tests ───────────────────────────────────────────────────────────


class TestSwarmState:
    def test_swarm_state_is_dataclass(self) -> None:
        """SwarmState must be a dataclass (has __dataclass_fields__)."""
        assert hasattr(SwarmState, "__dataclass_fields__")

    def test_swarm_state_field_names(self) -> None:
        """SwarmState must have exactly the specified fields."""
        field_names = {f.name for f in fields(SwarmState)}
        assert field_names == {
            "code_graph",
            "pheromone_cache",
            "config",
            "results",
            "degraded_agents",
        }

    def test_swarm_state_results_defaults_to_empty_list(self, tmp_path: Path) -> None:
        """results field defaults to an empty list."""
        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
        )
        assert state.results == []

    def test_swarm_state_degraded_agents_defaults_to_empty_list(
        self, tmp_path: Path
    ) -> None:
        """degraded_agents field defaults to an empty list."""
        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
        )
        assert state.degraded_agents == []

    def test_swarm_state_results_accepts_exploration_results(
        self, tmp_path: Path
    ) -> None:
        """results field accepts ExplorationResult instances."""
        result = _make_exploration_result()
        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
            results=[result],
        )
        assert len(state.results) == 1
        assert state.results[0] is result

    def test_swarm_state_degraded_agents_accepts_strings(self, tmp_path: Path) -> None:
        """degraded_agents field accepts string agent IDs."""
        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
            degraded_agents=["ant-1", "ant-2"],
        )
        assert state.degraded_agents == ["ant-1", "ant-2"]

    def test_swarm_state_independent_list_defaults(self, tmp_path: Path) -> None:
        """Two SwarmState instances must not share the same default list."""
        s1 = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path / "c1"),
            config=_make_config(),
        )
        s2 = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=_make_pheromone_cache(tmp_path / "c2"),
            config=_make_config(),
        )
        s1.results.append(_make_exploration_result())
        assert s2.results == [], "default list was shared across instances"


# ── SummaryStats tests ─────────────────────────────────────────────────────────


class TestSummaryStats:
    def test_summary_stats_valid(self) -> None:
        """SummaryStats accepts valid non-negative values."""
        stats = SummaryStats(
            total_functions_visited=10,
            total_bugs_found=3,
            unique_bugs=2,
            avg_confidence=0.85,
        )
        assert stats.total_functions_visited == 10
        assert stats.total_bugs_found == 3
        assert stats.unique_bugs == 2
        assert stats.avg_confidence == pytest.approx(0.85)

    def test_summary_stats_zero_values_allowed(self) -> None:
        """SummaryStats allows zero for all int fields and 0.0 for confidence."""
        stats = SummaryStats(
            total_functions_visited=0,
            total_bugs_found=0,
            unique_bugs=0,
            avg_confidence=0.0,
        )
        assert stats.total_functions_visited == 0

    def test_summary_stats_negative_functions_visited_rejected(self) -> None:
        """total_functions_visited must be >= 0."""
        with pytest.raises(ValidationError):
            SummaryStats(
                total_functions_visited=-1,
                total_bugs_found=0,
                unique_bugs=0,
                avg_confidence=0.0,
            )

    def test_summary_stats_negative_bugs_found_rejected(self) -> None:
        """total_bugs_found must be >= 0."""
        with pytest.raises(ValidationError):
            SummaryStats(
                total_functions_visited=0,
                total_bugs_found=-1,
                unique_bugs=0,
                avg_confidence=0.0,
            )

    def test_summary_stats_negative_unique_bugs_rejected(self) -> None:
        """unique_bugs must be >= 0."""
        with pytest.raises(ValidationError):
            SummaryStats(
                total_functions_visited=0,
                total_bugs_found=0,
                unique_bugs=-1,
                avg_confidence=0.0,
            )

    def test_summary_stats_avg_confidence_above_one_rejected(self) -> None:
        """avg_confidence must be <= 1.0."""
        with pytest.raises(ValidationError):
            SummaryStats(
                total_functions_visited=0,
                total_bugs_found=0,
                unique_bugs=0,
                avg_confidence=1.1,
            )

    def test_summary_stats_avg_confidence_negative_rejected(self) -> None:
        """avg_confidence must be >= 0.0."""
        with pytest.raises(ValidationError):
            SummaryStats(
                total_functions_visited=0,
                total_bugs_found=0,
                unique_bugs=0,
                avg_confidence=-0.1,
            )


# ── ReportMetadata tests ───────────────────────────────────────────────────────


class TestReportMetadata:
    def test_report_metadata_valid(self) -> None:
        """ReportMetadata accepts valid field values."""
        meta = ReportMetadata(
            repo_path="/home/user/project",
            agent_count=5,
            timestamp="2026-02-25T12:00:00Z",
            total_tokens=8192,
        )
        assert meta.repo_path == "/home/user/project"
        assert meta.agent_count == 5
        assert meta.timestamp == "2026-02-25T12:00:00Z"
        assert meta.total_tokens == 8192

    def test_report_metadata_agent_count_zero_rejected(self) -> None:
        """agent_count must be >= 1."""
        with pytest.raises(ValidationError):
            ReportMetadata(
                repo_path="/repo",
                agent_count=0,
                timestamp="2026-02-25T00:00:00Z",
                total_tokens=0,
            )

    def test_report_metadata_negative_agent_count_rejected(self) -> None:
        """agent_count must be >= 1 (negative also rejected)."""
        with pytest.raises(ValidationError):
            ReportMetadata(
                repo_path="/repo",
                agent_count=-1,
                timestamp="2026-02-25T00:00:00Z",
                total_tokens=0,
            )

    def test_report_metadata_negative_tokens_rejected(self) -> None:
        """total_tokens must be >= 0."""
        with pytest.raises(ValidationError):
            ReportMetadata(
                repo_path="/repo",
                agent_count=1,
                timestamp="2026-02-25T00:00:00Z",
                total_tokens=-1,
            )

    def test_report_metadata_zero_tokens_allowed(self) -> None:
        """total_tokens = 0 is valid."""
        meta = ReportMetadata(
            repo_path="/repo",
            agent_count=1,
            timestamp="now",
            total_tokens=0,
        )
        assert meta.total_tokens == 0


# ── AnalysisReport tests ───────────────────────────────────────────────────────


class TestAnalysisReport:
    def _make_valid_report(self) -> AnalysisReport:
        return AnalysisReport(
            bugs=[_make_bug_report()],
            summary_stats=SummaryStats(
                total_functions_visited=5,
                total_bugs_found=1,
                unique_bugs=1,
                avg_confidence=0.9,
            ),
            pheromone_heatmap={"foo": 45.0, "bar": 80.0},
            metadata=ReportMetadata(
                repo_path="/repo",
                agent_count=3,
                timestamp="2026-02-25T12:00:00Z",
                total_tokens=1024,
            ),
        )

    def test_analysis_report_valid(self) -> None:
        """AnalysisReport accepts a fully populated valid payload."""
        report = self._make_valid_report()
        assert len(report.bugs) == 1
        assert report.summary_stats.total_bugs_found == 1

    def test_analysis_report_bugs_is_list_of_bug_reports(self) -> None:
        """bugs field contains BugReport instances."""
        report = self._make_valid_report()
        assert all(isinstance(b, BugReport) for b in report.bugs)

    def test_analysis_report_empty_bugs_allowed(self) -> None:
        """bugs can be an empty list."""
        report = AnalysisReport(
            bugs=[],
            summary_stats=SummaryStats(
                total_functions_visited=0,
                total_bugs_found=0,
                unique_bugs=0,
                avg_confidence=0.0,
            ),
            pheromone_heatmap={},
            metadata=ReportMetadata(
                repo_path="/repo",
                agent_count=1,
                timestamp="now",
                total_tokens=0,
            ),
        )
        assert report.bugs == []

    def test_analysis_report_pheromone_heatmap_valid_range(self) -> None:
        """pheromone_heatmap values must be in [0.0, 100.0]."""
        report = AnalysisReport(
            bugs=[],
            summary_stats=SummaryStats(
                total_functions_visited=2,
                total_bugs_found=0,
                unique_bugs=0,
                avg_confidence=0.0,
            ),
            pheromone_heatmap={"fn_a": 0.0, "fn_b": 50.5, "fn_c": 100.0},
            metadata=ReportMetadata(
                repo_path="/repo",
                agent_count=1,
                timestamp="now",
                total_tokens=0,
            ),
        )
        for v in report.pheromone_heatmap.values():
            assert 0.0 <= v <= 100.0

    def test_analysis_report_pheromone_intensity_above_100_rejected(self) -> None:
        """pheromone_heatmap must reject intensity values above 100.0."""
        with pytest.raises(ValidationError):
            AnalysisReport(
                bugs=[],
                summary_stats=SummaryStats(
                    total_functions_visited=0,
                    total_bugs_found=0,
                    unique_bugs=0,
                    avg_confidence=0.0,
                ),
                pheromone_heatmap={"fn_a": 100.1},
                metadata=ReportMetadata(
                    repo_path="/repo",
                    agent_count=1,
                    timestamp="now",
                    total_tokens=0,
                ),
            )

    def test_analysis_report_pheromone_intensity_negative_rejected(self) -> None:
        """pheromone_heatmap must reject negative intensity values."""
        with pytest.raises(ValidationError):
            AnalysisReport(
                bugs=[],
                summary_stats=SummaryStats(
                    total_functions_visited=0,
                    total_bugs_found=0,
                    unique_bugs=0,
                    avg_confidence=0.0,
                ),
                pheromone_heatmap={"fn_a": -1.0},
                metadata=ReportMetadata(
                    repo_path="/repo",
                    agent_count=1,
                    timestamp="now",
                    total_tokens=0,
                ),
            )

    def test_analysis_report_round_trip_serialization(self) -> None:
        """AnalysisReport survives model_dump -> model_validate round-trip."""
        original = self._make_valid_report()
        dumped = original.model_dump()
        restored = AnalysisReport.model_validate(dumped)
        assert restored.model_dump() == dumped

    def test_analysis_report_nested_summary_stats(self) -> None:
        """summary_stats is a SummaryStats instance."""
        report = self._make_valid_report()
        assert isinstance(report.summary_stats, SummaryStats)

    def test_analysis_report_nested_metadata(self) -> None:
        """metadata is a ReportMetadata instance."""
        report = self._make_valid_report()
        assert isinstance(report.metadata, ReportMetadata)
