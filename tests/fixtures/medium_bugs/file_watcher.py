"""Filesystem watcher that triggers callbacks on file changes.

Polls a directory tree at a configurable interval and fires registered
callbacks when files are created, modified, or deleted.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ChangeCallback = Callable[[str, str], None]  # (event_type, path)


class FileWatcher:
    """Poll-based directory watcher with callback support."""

    def __init__(self, root: str | Path, interval: float = 1.0) -> None:
        self._root = Path(root)
        self._interval = interval
        self._callbacks: list[ChangeCallback] = []
        self._snapshot: dict[str, float] = {}
        self._running = False

    def register(self, callback: ChangeCallback) -> None:
        """Register a callback for file-change events."""
        self._callbacks.append(callback)

    def _take_snapshot(self) -> dict[str, float]:
        """Walk root and return {relative_path: mtime} for all files."""
        snap: dict[str, float] = {}
        for dirpath, _dirnames, filenames in os.walk(self._root):
            for fname in filenames:
                full = Path(dirpath) / fname
                try:
                    snap[str(full.relative_to(self._root))] = full.stat().st_mtime
                except OSError:
                    pass
        return snap

    def _fire(self, event: str, path: str) -> None:
        for cb in self._callbacks:
            try:  # BUG: bare-except sev=5
                cb(event, path)
            except:  # noqa: E722
                logger.warning("Callback raised an exception for event %s on %s", event, path)

    def _diff(
        self, old: dict[str, float], new: dict[str, float]
    ) -> list[tuple[str, str]]:
        events: list[tuple[str, str]] = []
        for path in new:
            if path not in old:
                events.append(("created", path))
            elif new[path] != old[path]:
                events.append(("modified", path))
        for path in old:
            if path not in new:
                events.append(("deleted", path))
        return events

    def run_once(self) -> list[tuple[str, str]]:
        """Take a single diff and fire callbacks. Returns list of events."""
        new_snap = self._take_snapshot()
        events = self._diff(self._snapshot, new_snap)
        for event, path in events:
            self._fire(event, path)
        self._snapshot = new_snap
        return events

    def start(self) -> None:
        """Block and poll indefinitely until stop() is called."""
        self._snapshot = self._take_snapshot()
        self._running = True
        while self._running:
            self.run_once()
            time.sleep(self._interval)

    def stop(self) -> None:
        self._running = False

    def watched_files(self) -> list[str]:
        """Return sorted list of currently tracked file paths."""
        return sorted(self._snapshot.keys())

    def stats(self) -> dict[str, Any]:
        return {
            "root": str(self._root),
            "interval": self._interval,
            "tracked_files": len(self._snapshot),
            "callbacks": len(self._callbacks),
        }
