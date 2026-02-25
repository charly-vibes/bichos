"""Token-bucket rate limiter.

Implements the token-bucket algorithm for rate-limiting API calls or any
resource access. Thread-safe via an internal lock.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class RateLimitExceeded(Exception):
    """Raised when a request is denied due to rate limiting."""

    key: str
    wait_seconds: float

    def __str__(self) -> str:
        return (
            f"Rate limit exceeded for {self.key!r}; "
            f"retry after {self.wait_seconds:.2f}s"
        )


class TokenBucket:
    """Token-bucket rate limiter for a single key."""

    def __init__(self, capacity: float, refill_rate: float) -> None:
        """
        Args:
            capacity: Maximum number of tokens in the bucket.
            refill_rate: Tokens added per second.
        """
        if capacity <= 0:
            raise ValueError(f"capacity must be > 0, got {capacity}")
        if refill_rate <= 0:
            raise ValueError(f"refill_rate must be > 0, got {refill_rate}")
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        added = elapsed * self._refill_rate
        self._tokens = min(self._capacity, self._tokens + added)
        self._last_refill = now

    def consume(self, tokens: float = 1.0) -> float:
        """Consume tokens from the bucket and return wait time (0 if allowed).

        Returns 0.0 if the request is allowed, or the number of seconds
        to wait before the next allowed request.
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0
            return (tokens - self._tokens) / self._refill_rate

    def allow(self, tokens: float = 1.0) -> bool:
        """Return True and consume tokens, or False without consuming."""
        return self.consume(tokens) == 0.0

    def require(self, key: str = "default", tokens: float = 1.0) -> None:
        """Consume tokens or raise RateLimitExceeded."""
        wait = self.consume(tokens)
        if wait > 0:
            raise RateLimitExceeded(key=key, wait_seconds=wait)

    @property
    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens


class MultiKeyRateLimiter:
    """Per-key token buckets with shared configuration."""

    def __init__(self, capacity: float, refill_rate: float) -> None:
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, key: str) -> TokenBucket:
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(self._capacity, self._refill_rate)
            return self._buckets[key]

    def allow(self, key: str, tokens: float = 1.0) -> bool:
        return self._get_bucket(key).allow(tokens)

    def require(self, key: str, tokens: float = 1.0) -> None:
        self._get_bucket(key).require(key=key, tokens=tokens)

    def active_keys(self) -> list[str]:
        with self._lock:
            return sorted(self._buckets.keys())
