"""Tests for the stigmergy pheromone system."""

from __future__ import annotations

from pathlib import Path

import pytest

from bichos.stigmergy.cache import PheromoneCache
from bichos.stigmergy.models import (
    BugPheromone,
    CurvaturePheromone,
    PheromoneType,
)


@pytest.fixture()
def cache(tmp_path: Path) -> PheromoneCache:
    return PheromoneCache(cache_dir=tmp_path / "cache", rho=0.1)


# ── Model tests ──────────────────────────────────────────────────────────────


def test_bug_pheromone_defaults() -> None:
    p = BugPheromone(
        key="bug:src/foo.py:divide",
        depositor="ant-1",
        severity=3,
        file_path="src/foo.py",
        function_name="divide",
        description="Division by zero",
    )
    assert p.pheromone_type == PheromoneType.BUG
    assert 0.0 <= p.intensity <= 100.0
    assert 1 <= p.severity <= 5


def test_pheromone_intensity_clamped() -> None:
    with pytest.raises(ValueError):
        BugPheromone(
            key="k",
            depositor="ant-1",
            intensity=200.0,  # out of range
            severity=1,
            file_path="f.py",
            function_name="fn",
            description="x",
        )


# ── Cache CRUD ────────────────────────────────────────────────────────────────


def test_deposit_and_get(cache: PheromoneCache) -> None:
    bug = BugPheromone(
        key="bug:src/calc.py:divide",
        depositor="ant-1",
        severity=3,
        file_path="src/calc.py",
        function_name="divide",
        description="Division by zero",
        intensity=5.0,
    )
    cache.deposit(bug)
    result = cache.get("bug:src/calc.py:divide")
    assert result is not None
    assert isinstance(result, BugPheromone)
    assert result.function_name == "divide"


def test_get_missing_returns_none(cache: PheromoneCache) -> None:
    assert cache.get("nonexistent:key") is None


def test_delete(cache: PheromoneCache) -> None:
    bug = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-1",
        severity=1,
        file_path="x.py",
        function_name="fn",
        description="d",
    )
    cache.deposit(bug)
    cache.delete("bug:x.py:fn")
    assert cache.get("bug:x.py:fn") is None


# ── Reinforcement ─────────────────────────────────────────────────────────────


def test_reinforcement_increases_intensity(cache: PheromoneCache) -> None:
    bug = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-1",
        severity=2,
        file_path="x.py",
        function_name="fn",
        description="d",
        intensity=10.0,
    )
    cache.deposit(bug)
    first_intensity = cache.get("bug:x.py:fn").intensity  # type: ignore[union-attr]

    bug2 = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-2",
        severity=2,
        file_path="x.py",
        function_name="fn",
        description="d",
        intensity=10.0,
    )
    cache.deposit(bug2)
    second_intensity = cache.get("bug:x.py:fn").intensity  # type: ignore[union-attr]
    assert second_intensity > first_intensity


def test_intensity_clamped_to_max(cache: PheromoneCache) -> None:
    bug = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-1",
        severity=5,
        file_path="x.py",
        function_name="fn",
        description="d",
        intensity=95.0,
    )
    cache.deposit(bug)
    # Re-deposit with high intensity — should not exceed 100
    bug.intensity = 50.0
    cache.deposit(bug)
    result = cache.get("bug:x.py:fn")
    assert result is not None
    assert result.intensity <= 100.0


# ── Evaporation ───────────────────────────────────────────────────────────────


def test_evaporate_reduces_intensity(cache: PheromoneCache) -> None:
    bug = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-1",
        severity=1,
        file_path="x.py",
        function_name="fn",
        description="d",
        intensity=50.0,
    )
    cache.deposit(bug)
    intensity_before = cache.get("bug:x.py:fn").intensity  # type: ignore[union-attr]
    cache.evaporate_all()
    intensity_after = cache.get("bug:x.py:fn").intensity  # type: ignore[union-attr]
    assert intensity_after < intensity_before


def test_evaporate_prunes_below_min(tmp_path: Path) -> None:
    c = PheromoneCache(
        cache_dir=tmp_path / "prune",
        rho=0.99,
        min_intensity=1.0,
    )
    bug = BugPheromone(
        key="bug:x.py:fn",
        depositor="ant-1",
        severity=1,
        file_path="x.py",
        function_name="fn",
        description="d",
        intensity=1.0,
    )
    c.deposit(bug)
    pruned = c.evaporate_all()
    assert pruned >= 1
    assert c.get("bug:x.py:fn") is None


# ── Querying ──────────────────────────────────────────────────────────────────


def test_iter_by_type(cache: PheromoneCache) -> None:
    for i in range(3):
        cache.deposit(
            BugPheromone(
                key=f"bug:f{i}.py:fn",
                depositor="ant-1",
                severity=1,
                file_path=f"f{i}.py",
                function_name="fn",
                description="d",
            )
        )
    cache.deposit(
        CurvaturePheromone(
            key="curvature:f0.py:fn",
            depositor="ant-1",
            complexity=10,
            loc=50,
            file_path="f0.py",
        )
    )
    bugs = list(cache.iter_by_type(PheromoneType.BUG))
    assert len(bugs) == 3


def test_top_by_intensity(cache: PheromoneCache) -> None:
    for i, intensity in enumerate([80.0, 50.0, 20.0]):
        cache.deposit(
            BugPheromone(
                key=f"bug:f{i}.py:fn",
                depositor="ant-1",
                severity=1,
                file_path=f"f{i}.py",
                function_name="fn",
                description="d",
                intensity=intensity,
            )
        )
    top = cache.top_by_intensity(PheromoneType.BUG, n=2)
    assert len(top) == 2
    assert top[0].intensity >= top[1].intensity


def test_stats(cache: PheromoneCache) -> None:
    cache.deposit(
        BugPheromone(
            key="bug:a.py:fn",
            depositor="ant-1",
            severity=1,
            file_path="a.py",
            function_name="fn",
            description="d",
        )
    )
    s = cache.stats()
    assert s["bug"] == 1
    assert s["curvature"] == 0
