"""PheromoneCache — diskcache-backed persistent pheromone store."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from pathlib import Path

import diskcache

from bichos.stigmergy.models import (
    AlertPheromone,
    BugPheromone,
    CurvaturePheromone,
    PerformancePheromone,
    Pheromone,
    PheromoneType,
)

_DEFAULT_TTLS: dict[PheromoneType, int] = {
    PheromoneType.BUG: 86400,
    PheromoneType.CURVATURE: 3600,
    PheromoneType.PERFORMANCE: 1800,
    PheromoneType.ALERT: 604800,
}

AnyPheromone = BugPheromone | CurvaturePheromone | PerformancePheromone | AlertPheromone


class PheromoneCache:
    """Persistent pheromone grid backed by diskcache.

    Thread-safe for concurrent ant agents. All read/write operations are
    serialised at the diskcache level.
    """

    def __init__(
        self,
        cache_dir: Path | str = ".bichos_cache",
        rho: float = 0.1,
        ttls: dict[PheromoneType, int] | None = None,
        max_intensity: float = 100.0,
        min_intensity: float = 0.01,
    ) -> None:
        self._cache = diskcache.Cache(str(cache_dir))
        self._rho = rho
        self._ttls = {**_DEFAULT_TTLS, **(ttls or {})}
        self._max = max_intensity
        self._min = min_intensity
        self._lock = threading.Lock()

    # ── CRUD ──────────────────────────────────────────────────────────────

    def deposit(self, pheromone: AnyPheromone) -> None:
        """Deposit (or reinforce) a pheromone at its key.

        If a pheromone already exists at the key the intensity is updated
        using the ACO formula: τ(t+1) = (1-ρ)·τ(t) + Δτ.
        A fresh deposit uses the pheromone's intensity as Δτ.
        """
        ttl = self._ttls.get(pheromone.pheromone_type, 3600)
        key = pheromone.key

        with self._lock:
            existing: AnyPheromone | None = self._cache.get(key)  # type: ignore[assignment]
            if existing is not None:
                new_intensity = (
                    1.0 - self._rho
                ) * existing.intensity + pheromone.intensity
                pheromone.intensity = max(self._min, min(self._max, new_intensity))
            self._cache.set(key, pheromone, expire=ttl)

    def get(self, key: str) -> AnyPheromone | None:
        """Retrieve a pheromone by key, or None if absent/expired."""
        return self._cache.get(key)  # type: ignore[return-value]

    def delete(self, key: str) -> None:
        """Remove a pheromone from the cache."""
        with self._lock:
            self._cache.delete(key)

    def evaporate_all(self) -> int:
        """Apply evaporation decay to every entry in the cache.

        Entries whose intensity drops below *min_intensity* are pruned.

        Returns:
            Number of entries pruned.
        """
        pruned = 0
        keys = list(self._cache.iterkeys())
        for key in keys:
            with self._lock:
                entry: AnyPheromone | None = self._cache.get(key)  # type: ignore[assignment]
                if entry is None:
                    continue
                new_intensity = (1.0 - self._rho) * entry.intensity
                if new_intensity < self._min:
                    self._cache.delete(key)
                    pruned += 1
                else:
                    entry.intensity = new_intensity
                    ttl = self._ttls.get(entry.pheromone_type, 3600)
                    self._cache.set(key, entry, expire=ttl)
        return pruned

    # ── Querying ──────────────────────────────────────────────────────────

    def iter_by_type(self, pheromone_type: PheromoneType) -> Iterator[AnyPheromone]:
        """Iterate over all live pheromones of a given type."""
        for key in self._cache.iterkeys():
            entry: AnyPheromone | None = self._cache.get(key)  # type: ignore[assignment]
            if entry is not None and entry.pheromone_type == pheromone_type:
                yield entry

    def top_by_intensity(
        self, pheromone_type: PheromoneType, n: int = 10
    ) -> list[AnyPheromone]:
        """Return the *n* highest-intensity pheromones of a given type."""
        entries = list(self.iter_by_type(pheromone_type))
        entries.sort(key=lambda e: e.intensity, reverse=True)
        return entries[:n]

    def stats(self) -> dict[str, int]:
        """Return entry counts per pheromone type."""
        counts: dict[str, int] = {t.value: 0 for t in PheromoneType}
        for key in self._cache.iterkeys():
            entry: Pheromone | None = self._cache.get(key)  # type: ignore[assignment]
            if entry is not None:
                counts[entry.pheromone_type.value] += 1
        return counts

    def close(self) -> None:
        self._cache.close()

    def __enter__(self) -> PheromoneCache:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
