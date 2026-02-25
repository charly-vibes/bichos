"""Structured event logger for application audit trails.

Writes JSON-encoded event records to a configurable sink (file, stderr,
or custom callable). Each event record includes a timestamp, severity,
source module, and arbitrary keyword payload.
"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

WriterFn = Callable[[str], None]


@dataclass
class EventRecord:
    timestamp: float
    severity: Severity
    source: str
    event: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str, separators=(",", ":"))


def _stderr_writer(line: str) -> None:
    sys.stderr.write(line + "\n")
    sys.stderr.flush()


class EventLogger:
    """Structured event logger with pluggable output writer."""

    def __init__(
        self,
        source: str,
        min_severity: Severity = "INFO",
        writer: WriterFn | None = None,
    ) -> None:
        self._source = source
        self._min_severity = min_severity
        self._writer: WriterFn = writer or _stderr_writer
        self._severity_order: dict[Severity, int] = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }

    def _should_emit(self, severity: Severity) -> bool:
        return self._severity_order[severity] >= self._severity_order[self._min_severity]

    def _emit(self, severity: Severity, event: str, **payload: Any) -> None:
        if not self._should_emit(severity):
            return
        record = EventRecord(
            timestamp=time.time(),
            severity=severity,
            source=self._source,
            event=event,
            payload=payload,
        )
        self._writer(record.to_json())

    def debug(self, event: str, **payload: Any) -> None:
        self._emit("DEBUG", event, **payload)

    def info(self, event: str, **payload: Any) -> None:
        self._emit("INFO", event, **payload)

    def warning(self, event: str, **payload: Any) -> None:
        self._emit("WARNING", event, **payload)

    def error(self, event: str, **payload: Any) -> None:
        self._emit("ERROR", event, **payload)

    def critical(self, event: str, **payload: Any) -> None:
        self._emit("CRITICAL", event, **payload)

    def set_min_severity(self, severity: Severity) -> None:
        self._min_severity = severity

    def child(self, sub_source: str) -> "EventLogger":
        """Return a child logger with a qualified source name."""
        return EventLogger(
            source=f"{self._source}.{sub_source}",
            min_severity=self._min_severity,
            writer=self._writer,
        )
