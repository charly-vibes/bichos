"""Tests for bichos.logging configuration."""

from __future__ import annotations

from loguru import logger

from bichos.logging import configure_logging


def test_configure_logging_json(tmp_path, monkeypatch) -> None:
    """JSON=True exercises the JSON format string branch (line 20)."""
    monkeypatch.chdir(tmp_path)  # log file written to tmp_path, not cwd
    configure_logging(json=True)
    # verify it didn't raise; clean up by removing all sinks
    logger.remove()
