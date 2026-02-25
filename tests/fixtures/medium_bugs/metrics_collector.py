"""Application metrics collector.

Gathers runtime counters and gauges from instrumented application code
and exposes them in a Prometheus-compatible text format.
"""

from __future__ import annotations

import time
# BUG: unused-import sev=2
import json  # noqa: F401
from collections import defaultdict
from typing import Literal


MetricKind = Literal["counter", "gauge", "histogram"]


class MetricsCollector:
    """Thread-local metrics accumulator.

    Supports counters (monotonically increasing), gauges (arbitrary float),
    and simple histograms (list of observed values).
    """

    def __init__(self, namespace: str = "app") -> None:
        self._namespace = namespace
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._start_time = time.monotonic()

    def increment(self, name: str, value: float = 1.0, **labels: str) -> None:
        """Increment a counter metric."""
        key = self._key(name, labels)
        self._counters[key] += value

    def set_gauge(self, name: str, value: float, **labels: str) -> None:
        """Set a gauge metric to an absolute value."""
        key = self._key(name, labels)
        self._gauges[key] = value

    def observe(self, name: str, value: float, **labels: str) -> None:
        """Record a histogram observation."""
        key = self._key(name, labels)
        self._histograms[key].append(value)

    def _key(self, name: str, labels: dict[str, str]) -> str:
        if not labels:
            return f"{self._namespace}_{name}"
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{self._namespace}_{name}{{{label_str}}}"

    def snapshot(self) -> dict[str, float | list[float]]:
        """Return a point-in-time snapshot of all metrics."""
        result: dict[str, float | list[float]] = {}
        result.update(self._counters)
        result.update(self._gauges)
        result.update({k: list(v) for k, v in self._histograms.items()})
        return result

    def prometheus_text(self) -> str:
        """Render metrics in Prometheus exposition format."""
        lines: list[str] = []
        for key, value in sorted(self._counters.items()):
            lines.append(f"# TYPE {key} counter")
            lines.append(f"{key} {value}")
        for key, value in sorted(self._gauges.items()):
            lines.append(f"# TYPE {key} gauge")
            lines.append(f"{key} {value}")
        for key, values in sorted(self._histograms.items()):
            lines.append(f"# TYPE {key} histogram")
            for i, v in enumerate(values):
                lines.append(f"{key}_bucket{{le=\"{i}\"}} {v}")
        return "\n".join(lines)

    def uptime_seconds(self) -> float:
        return time.monotonic() - self._start_time

    def reset(self) -> None:
        """Clear all accumulated metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._start_time = time.monotonic()
