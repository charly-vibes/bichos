"""Background job queue with worker threads.

Jobs are submitted by any thread and processed by a pool of worker
threads. The job registry tracks active and completed jobs.
"""

from __future__ import annotations

import queue
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Job:
    job_id: str
    func: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    result: Any = None
    error: str | None = None


class JobQueue:
    """Multi-threaded job queue with shared mutable state."""

    def __init__(self, workers: int = 4) -> None:
        self._q: queue.Queue[Job] = queue.Queue()
        self._workers = workers
        # BUG: race-condition sev=8
        self._registry: dict[str, Job] = {}  # mutated from multiple threads without lock
        self._threads: list[threading.Thread] = []
        self._running = False

    def start(self) -> None:
        """Spawn worker threads."""
        self._running = True
        for _ in range(self._workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        """Signal workers to stop and wait for them."""
        self._running = False
        for _ in self._threads:
            self._q.put_nowait(None)  # type: ignore[arg-type]
        for t in self._threads:
            t.join(timeout=5.0)
        self._threads.clear()

    def submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        """Enqueue a job and return its ID."""
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id, func=func, args=args, kwargs=kwargs)
        self._registry[job_id] = job  # unsynchronised write
        self._q.put(job)
        return job_id

    def status(self, job_id: str) -> str | None:
        """Return current status of the job, or None if unknown."""
        job = self._registry.get(job_id)
        return job.status if job else None

    def result(self, job_id: str) -> Any:
        """Return the job result, or None if not yet complete."""
        job = self._registry.get(job_id)
        return job.result if job else None

    def _worker_loop(self) -> None:
        while self._running:
            try:
                job = self._q.get(timeout=1.0)
            except queue.Empty:
                continue
            if job is None:
                break
            job.status = "running"  # unsynchronised write
            try:
                job.result = job.func(*job.args, **job.kwargs)
                job.status = "done"
            except Exception as exc:  # noqa: BLE001
                job.error = str(exc)
                job.status = "failed"
            finally:
                self._q.task_done()

    def pending_count(self) -> int:
        return self._q.qsize()

    def all_jobs(self) -> list[Job]:
        return list(self._registry.values())
