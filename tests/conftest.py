"""Shared pytest fixtures for bichos test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SIMPLE_BUGS_DIR = FIXTURES_DIR / "simple_bugs"


@pytest.fixture()
def simple_bugs_path() -> Path:
    """Path to the simple_bugs fixture directory."""
    return SIMPLE_BUGS_DIR


@pytest.fixture()
def default_config():  # type: ignore[return]
    """Return a default HiveConfig instance."""
    from bichos.config import HiveConfig

    return HiveConfig.default()
