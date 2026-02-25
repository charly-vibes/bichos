"""Loguru logging configuration for bichos."""

from __future__ import annotations

import sys

from loguru import logger


def configure_logging(level: str = "INFO", json: bool = False) -> None:
    """Configure Loguru for the bichos process.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR).
        json: Emit structured JSON logs instead of human-readable output.
    """
    logger.remove()

    if json:
        fmt = (
            '{{"time":"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}",'
            '"level":"{level}",'
            '"name":"{name}",'
            '"message":"{message}"}}'
        )
    else:
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        )

    logger.add(sys.stderr, level=level, format=fmt, colorize=not json)
    logger.add(
        "bichos_{time:YYYYMMDD}.log",
        level="DEBUG",
        format=fmt,
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        serialize=json,
    )
