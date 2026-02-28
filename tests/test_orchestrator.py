"""Tests for hive orchestrator data models (bichos-46o) and workflow (bichos-bgc).

Tests cover:
- SwarmState dataclass fields and defaults
- SummaryStats Pydantic model with ge=0 constraints
- ReportMetadata Pydantic model field constraints
- AnalysisReport Pydantic model with nested models
- pheromone_heatmap intensity values in [0.0, 100.0]
- confidence values in [0.0, 1.0]
- Round-trip serialization of AnalysisReport
- InitNode builds CodeGraph + PheromoneCache and stores them on state
- SplitNode spawns correct number of agents (mocked)
- JoinNode deduplicates bugs by (file_path, line_number)
- Full pipeline with mocked LLM via run_hive
- Agent failure and timeout resilience
"""

from dataclasses import fields
from pathlib import Path
from unittest.mock import AsyncMock, patch

import networkx as nx
import pytest
from pydantic import ValidationError
from pydantic_graph import End, GraphRunContext

from bichos.agents.ant.models import BugReport, ExplorationResult
from bichos.config import HiveConfig
from bichos.graph.models import CodeGraph, NodeMeta
from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats, SwarmState
from bichos.hive.orchestrator import InitNode, JoinNode, ReportNode, SplitNode, run_hive
from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import BugPheromone

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


# ── Orchestrator workflow tests (bichos-bgc) ──────────────────────────────────


def _make_swarm_state(tmp_path: Path) -> SwarmState:
    """Return a minimal SwarmState with an empty graph and fresh cache."""
    return SwarmState(
        code_graph=_make_code_graph(),
        pheromone_cache=_make_pheromone_cache(tmp_path),
        config=_make_config(),
    )


class TestInitNode:
    """InitNode must build CodeGraph + PheromoneCache and store them on state."""

    @pytest.mark.asyncio
    async def test_init_node_populates_state(self, tmp_path: Path) -> None:
        """After InitNode.run, state.code_graph has a node count >= 0."""
        state = _make_swarm_state(tmp_path)
        node = InitNode(repo_path=tmp_path, cache_dir=tmp_path / "cache")

        ctx = GraphRunContext(state=state, deps=None)

        next_node = await node.run(ctx)

        # state must now contain real CodeGraph and PheromoneCache instances
        assert isinstance(state.code_graph, CodeGraph)
        assert isinstance(state.pheromone_cache, PheromoneCache)
        # should transition to SplitNode
        assert isinstance(next_node, SplitNode)

    @pytest.mark.asyncio
    async def test_init_node_accepts_real_python_dir(self, tmp_path: Path) -> None:
        """InitNode builds a graph from a directory containing .py files."""
        # Write a small Python file
        (tmp_path / "sample.py").write_text("def hello():\n    pass\n")
        state = _make_swarm_state(tmp_path)
        node = InitNode(repo_path=tmp_path, cache_dir=tmp_path / "cache")

        ctx = GraphRunContext(state=state, deps=None)
        await node.run(ctx)

        assert state.code_graph.node_count() >= 1


class TestSplitNode:
    """SplitNode must spawn one agent per function node and handle failures."""

    @pytest.mark.asyncio
    async def test_split_node_spawns_correct_count(self, tmp_path: Path) -> None:
        """SplitNode calls run_ant once per function node in the graph."""
        g: nx.DiGraph[str] = nx.DiGraph()
        for i in range(3):
            qname = f"mod.fn{i}"
            meta = NodeMeta(
                name=f"fn{i}",
                qualified_name=qname,
                file_path="mod.py",
                lineno=i + 1,
                loc=5,
                complexity=1,
                is_class=False,
            )
            g.add_node(qname, meta=meta)

        state = SwarmState(
            code_graph=CodeGraph(graph=g, root=tmp_path),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
        )

        fake_result = ExplorationResult(
            path_visited=["mod.fn0"],
            bugs_found=[],
            tokens_used=10,
        )

        with patch(
            "bichos.hive.orchestrator.run_ant",
            new_callable=AsyncMock,
            return_value=fake_result,
        ) as mock_run_ant:
            node = SplitNode()
            ctx = GraphRunContext(state=state, deps=None)
            next_node = await node.run(ctx)

        assert mock_run_ant.call_count == 3
        assert isinstance(next_node, JoinNode)
        assert len(state.results) == 3

    @pytest.mark.asyncio
    async def test_split_node_handles_exception(self, tmp_path: Path) -> None:
        """A failing agent adds its ID to degraded_agents; swarm continues."""
        g: nx.DiGraph[str] = nx.DiGraph()
        for i in range(2):
            qname = f"mod.fn{i}"
            meta = NodeMeta(
                name=f"fn{i}",
                qualified_name=qname,
                file_path="mod.py",
                lineno=i + 1,
                loc=5,
                complexity=1,
                is_class=False,
            )
            g.add_node(qname, meta=meta)

        state = SwarmState(
            code_graph=CodeGraph(graph=g, root=tmp_path),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
        )

        fake_result = ExplorationResult(
            path_visited=["mod.fn0"],
            bugs_found=[],
            tokens_used=10,
        )

        call_count = 0

        async def side_effect(*args: object, **kwargs: object) -> ExplorationResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("agent failure")
            return fake_result

        with patch("bichos.hive.orchestrator.run_ant", side_effect=side_effect):
            node = SplitNode()
            ctx = GraphRunContext(state=state, deps=None)
            await node.run(ctx)

        # One result succeeded, one degraded
        assert len(state.results) == 1
        assert len(state.degraded_agents) == 1

    @pytest.mark.asyncio
    async def test_agent_timeout_enforced(self, tmp_path: Path) -> None:
        """An agent that times out is treated as degraded, not a crash."""
        g: nx.DiGraph[str] = nx.DiGraph()
        qname = "mod.slow_fn"
        meta = NodeMeta(
            name="slow_fn",
            qualified_name=qname,
            file_path="mod.py",
            lineno=1,
            loc=5,
            complexity=1,
            is_class=False,
        )
        g.add_node(qname, meta=meta)

        state = SwarmState(
            code_graph=CodeGraph(graph=g, root=tmp_path),
            pheromone_cache=_make_pheromone_cache(tmp_path),
            config=_make_config(),
        )

        async def slow_agent(*args: object, **kwargs: object) -> ExplorationResult:
            raise TimeoutError()

        with patch("bichos.hive.orchestrator.run_ant", side_effect=slow_agent):
            node = SplitNode()
            ctx = GraphRunContext(state=state, deps=None)
            await node.run(ctx)

        assert len(state.results) == 0
        assert len(state.degraded_agents) == 1


class TestJoinNode:
    """JoinNode must deduplicate bugs by (file_path, line_number)."""

    @pytest.mark.asyncio
    async def test_join_node_deduplicates_by_location(self, tmp_path: Path) -> None:
        """Two bugs at the same (file_path, line_number) → one in state."""
        dup_bug = BugReport(
            function_name="foo",
            file_path="src/foo.py",
            line_number=10,
            description="duplicate",
            severity=5,
            confidence=0.8,
        )
        dup_bug2 = BugReport(
            function_name="foo",
            file_path="src/foo.py",
            line_number=10,
            description="duplicate again",
            severity=4,
            confidence=0.6,
        )
        r1 = ExplorationResult(path_visited=["foo"], bugs_found=[dup_bug])
        r2 = ExplorationResult(path_visited=["bar"], bugs_found=[dup_bug2])

        state = _make_swarm_state(tmp_path)
        state.results = [r1, r2]

        node = JoinNode()
        ctx = GraphRunContext(state=state, deps=None)
        next_node = await node.run(ctx)

        assert isinstance(next_node, ReportNode)
        # deduplicated list stored on state — access via attribute
        assert len(next_node.deduplicated_bugs) == 1

    @pytest.mark.asyncio
    async def test_join_node_keeps_highest_confidence(self, tmp_path: Path) -> None:
        """When deduplicating, the bug with the highest confidence wins."""
        low_conf = BugReport(
            function_name="foo",
            file_path="src/foo.py",
            line_number=10,
            description="low confidence",
            severity=3,
            confidence=0.5,
        )
        high_conf = BugReport(
            function_name="foo",
            file_path="src/foo.py",
            line_number=10,
            description="high confidence",
            severity=7,
            confidence=0.95,
        )
        r1 = ExplorationResult(path_visited=["foo"], bugs_found=[low_conf])
        r2 = ExplorationResult(path_visited=["bar"], bugs_found=[high_conf])

        state = _make_swarm_state(tmp_path)
        state.results = [r1, r2]

        node = JoinNode()
        ctx = GraphRunContext(state=state, deps=None)
        next_node = await node.run(ctx)

        assert next_node.deduplicated_bugs[0].confidence == pytest.approx(0.95)


class TestReportNode:
    """ReportNode must return End(AnalysisReport) with correct stats."""

    @pytest.mark.asyncio
    async def test_report_node_builds_analysis_report(self, tmp_path: Path) -> None:
        """ReportNode returns End(AnalysisReport) with correct stats."""
        bug = BugReport(
            function_name="foo",
            file_path="src/foo.py",
            line_number=10,
            description="A bug",
            severity=5,
            confidence=0.9,
        )
        result = ExplorationResult(
            path_visited=["foo", "bar"],
            bugs_found=[bug],
            tokens_used=50,
        )

        state = _make_swarm_state(tmp_path)
        state.results = [result]

        deduped = [bug]
        node = ReportNode(
            deduplicated_bugs=deduped,
            repo_path=tmp_path,
        )
        ctx = GraphRunContext(state=state, deps=None)
        end = await node.run(ctx)

        assert isinstance(end, End)
        report = end.data
        assert isinstance(report, AnalysisReport)
        assert len(report.bugs) == 1
        assert report.summary_stats.unique_bugs == 1
        assert report.metadata.total_tokens >= 0
        assert report.metadata.agent_count >= 1
        assert all(0.0 <= v <= 100.0 for v in report.pheromone_heatmap.values())

    @pytest.mark.asyncio
    async def test_heatmap_single_bug_pheromone(self, tmp_path: Path) -> None:
        """A single BugPheromone deposited in the cache appears in the heatmap."""
        cache = _make_pheromone_cache(tmp_path)
        pheromone = BugPheromone(
            key="bug:foo.bar:1",
            depositor="ant-0",
            severity=3,
            file_path="src/foo.py",
            function_name="foo.bar",
            description="SQL injection risk",
            intensity=50.0,
        )
        cache.deposit(pheromone)

        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=cache,
            config=_make_config(),
        )
        node = ReportNode(deduplicated_bugs=[], repo_path=tmp_path)
        ctx = GraphRunContext(state=state, deps=None)
        end = await node.run(ctx)

        report = end.data
        assert "foo.bar" in report.pheromone_heatmap
        assert report.pheromone_heatmap["foo.bar"] == pytest.approx(50.0)

    @pytest.mark.asyncio
    async def test_heatmap_accumulates_two_pheromones_at_same_location(
        self, tmp_path: Path
    ) -> None:
        """Two BugPheromones sharing function_name but with distinct keys accumulate."""
        cache = _make_pheromone_cache(tmp_path)
        p1 = BugPheromone(
            key="bug:foo.bar:1",
            depositor="ant-0",
            severity=2,
            file_path="src/foo.py",
            function_name="foo.bar",
            description="First finding",
            intensity=30.0,
        )
        p2 = BugPheromone(
            key="bug:foo.bar:2",
            depositor="ant-1",
            severity=4,
            file_path="src/foo.py",
            function_name="foo.bar",
            description="Second finding",
            intensity=40.0,
        )
        cache.deposit(p1)
        cache.deposit(p2)

        state = SwarmState(
            code_graph=_make_code_graph(),
            pheromone_cache=cache,
            config=_make_config(),
        )
        node = ReportNode(deduplicated_bugs=[], repo_path=tmp_path)
        ctx = GraphRunContext(state=state, deps=None)
        end = await node.run(ctx)

        report = end.data
        assert "foo.bar" in report.pheromone_heatmap
        assert report.pheromone_heatmap["foo.bar"] == pytest.approx(70.0)


class TestRunHive:
    """Full pipeline integration tests using mocked LLM."""

    @pytest.mark.asyncio
    async def test_full_pipeline_mocked_llm(self, tmp_path: Path) -> None:
        """run_hive returns AnalysisReport without calling real LLM."""
        (tmp_path / "sample.py").write_text("def hello():\n    pass\n")

        fake_result = ExplorationResult(
            path_visited=["sample.hello"],
            bugs_found=[
                BugReport(
                    function_name="hello",
                    file_path="sample.py",
                    line_number=1,
                    description="Fake bug",
                    severity=3,
                    confidence=0.8,
                )
            ],
            tokens_used=100,
        )

        config = HiveConfig.default()
        with patch(
            "bichos.hive.orchestrator.run_ant",
            new_callable=AsyncMock,
            return_value=fake_result,
        ):
            report = await run_hive(tmp_path, config)

        assert isinstance(report, AnalysisReport)
        assert report.metadata.repo_path == str(tmp_path)

    @pytest.mark.asyncio
    async def test_full_pipeline_agent_failure_does_not_crash(
        self, tmp_path: Path
    ) -> None:
        """run_hive returns AnalysisReport even if all agents fail."""
        (tmp_path / "sample.py").write_text("def hello():\n    pass\n")

        config = HiveConfig.default()
        with patch(
            "bichos.hive.orchestrator.run_ant",
            new_callable=AsyncMock,
            side_effect=RuntimeError("all agents dead"),
        ):
            report = await run_hive(tmp_path, config)

        assert isinstance(report, AnalysisReport)
        assert report.bugs == []
