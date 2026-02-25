"""In-process session cache backed by a plain dict.

Stores active session tokens and their associated metadata.
Designed for single-process web workers; not suitable for multi-process
deployments without an external store.
"""

from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Any


class SessionCache:
    """Thread-unsafe session store.

    Sessions are keyed by token string and held in a shared dict that is
    mutated directly from any thread without synchronisation.
    """

    _sessions: dict[str, dict[str, Any]] = {}  # shared across all instances

    def __init__(self, default_ttl_seconds: int = 1800) -> None:
        self._ttl = timedelta(seconds=default_ttl_seconds)

    def put(self, token: str, data: dict[str, Any]) -> None:
        """Store or refresh a session entry."""
        expiry = datetime.utcnow() + self._ttl
        # BUG: race-condition sev=8
        self._sessions[token] = {**data, "_expiry": expiry}  # noqa: RUF012

    def get(self, token: str) -> dict[str, Any] | None:
        """Retrieve a session by token; returns None if missing or expired."""
        entry = self._sessions.get(token)
        if entry is None:
            return None
        if datetime.utcnow() > entry["_expiry"]:
            self.delete(token)
            return None
        return {k: v for k, v in entry.items() if k != "_expiry"}

    def delete(self, token: str) -> None:
        self._sessions.pop(token, None)

    def purge_expired(self) -> int:
        """Remove all expired sessions and return the count removed."""
        now = datetime.utcnow()
        expired = [t for t, d in self._sessions.items() if now > d["_expiry"]]
        for token in expired:
            self._sessions.pop(token, None)
        return len(expired)

    def active_count(self) -> int:
        self.purge_expired()
        return len(self._sessions)


def _warm_up_worker(cache: SessionCache, prefix: str, n: int) -> None:
    """Populate the cache from a background thread (demonstrates the race)."""
    for i in range(n):
        cache.put(f"{prefix}-{i}", {"user_id": i, "role": "viewer"})


def preload_sessions(n: int = 50) -> SessionCache:
    """Spawn two threads that concurrently write to the same cache."""
    cache = SessionCache()
    t1 = threading.Thread(target=_warm_up_worker, args=(cache, "alpha", n))
    t2 = threading.Thread(target=_warm_up_worker, args=(cache, "beta", n))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return cache
