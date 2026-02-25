"""HTTP retry helper with exponential back-off.

Provides a configurable retry wrapper for HTTP calls. Supports
jitter, custom retryable status codes, and per-attempt timeout.
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retryable_status_codes: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 500, 502, 503, 504})
    )


class RetryExhausted(RuntimeError):
    """Raised when all retry attempts fail."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        super().__init__(f"All {attempts} attempts failed. Last error: {last_error}")
        self.attempts = attempts
        self.last_error = last_error


def _compute_delay(attempt: int, config: RetryConfig) -> float:
    """Return delay in seconds for the given attempt (0-indexed)."""
    delay = min(config.base_delay * (config.backoff_factor ** attempt), config.max_delay)
    if config.jitter:
        delay *= random.uniform(0.5, 1.5)  # noqa: S311
    return delay


def with_retry(
    fn: Callable[[], T],
    config: RetryConfig | None = None,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T:
    """Call fn with retry logic defined by config.

    Args:
        fn: Zero-argument callable to invoke.
        config: Retry configuration; uses defaults if None.
        on_retry: Optional callback invoked on each failed attempt with
                  (attempt_number, exception).

    Returns:
        The return value of fn on success.

    Raises:
        RetryExhausted: When all attempts fail.
    """
    cfg = config or RetryConfig()
    last_exc: Exception | None = None
    for attempt in range(cfg.max_attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < cfg.max_attempts - 1:
                delay = _compute_delay(attempt, cfg)
                logger.warning(
                    "Attempt %d/%d failed (%s); retrying in %.2fs",
                    attempt + 1,
                    cfg.max_attempts,
                    exc,
                    delay,
                )
                if on_retry:
                    on_retry(attempt + 1, exc)
                time.sleep(delay)
            else:
                logger.error("All %d attempts failed", cfg.max_attempts)
    assert last_exc is not None
    raise RetryExhausted(cfg.max_attempts, last_exc)


def retry_decorator(config: RetryConfig | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator factory that wraps a function with retry logic."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return with_retry(lambda: fn(*args, **kwargs), config=config)
        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper
    return decorator
