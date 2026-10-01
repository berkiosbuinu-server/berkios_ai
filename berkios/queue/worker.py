from __future__ import annotations

import asyncio
import os
import socket
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .models import Job, JobState


@dataclass
class WorkerConfig:
    lease_seconds: int = 60
    heartbeat_seconds: int = 20
    poll_timeout_seconds: int = 2


class JobWorker:
    """
    Multi-worker Redis queue consumer with a renewable lease.

    A running job is periodically heartbeated. If the worker disappears,
    a recovery process can requeue the expired lease. The worker also stops
    heartbeating before acknowledging completion, so durable state remains
    the source of truth.
    """

    def __init__(
        self,
        queue: Any,
        persistence: Any,
        handlers: Mapping[str, Callable[[Job], Any]] | None = None,
        config: WorkerConfig | None = None,
        worker_id: str | None = None,
    ):
        self.queue = queue
        self.event_callback = None
        # Legacy/simple mode: (queue, handlers, callback), no persistence.
        if isinstance(persistence, Mapping):
            if callable(handlers):
                self.event_callback = handlers
            handlers = persistence
            persistence = None
        self.persistence = persistence
        self.handlers = dict(handlers or {})
        self.config = config or WorkerConfig()
        self.worker_id = worker_id or (
            f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        self._stop = threading.Event()

    def _notify(self, event, job):
        if self.event_callback is not None:
            self.event_callback(event, job)

    def stop(self) -> None:
        self._stop.set()

    def _heartbeat_loop(self, job_id: str) -> None:
        interval = max(1, self.config.heartbeat_seconds)
        while not self._stop.wait(interval):
            try:
                self.persistence.heartbeat_job(
                    job_id,
                    worker_id=self.worker_id,
                    lease_seconds=self.config.lease_seconds,
                )
            except Exception:
                # The main execution path remains responsible for final state.
                # A recovery pass can reclaim the job if heartbeats stop.
                continue

    def run_once(self) -> bool:
        job = self.queue.dequeue(timeout=self.config.poll_timeout_seconds)
        if job is None:
            return False
        if isinstance(job, dict):
            job = Job.from_dict(job)

        if self.persistence is None:
            self._notify("job.started", job)
            try:
                handler = self.handlers.get(job.kind)
                if handler is None:
                    raise KeyError(f"No handler registered for job kind: {job.kind}")
                try:
                    result = handler(job.payload)
                except (TypeError, AttributeError):
                    result = handler(job)
                job.result = result
                job.state = JobState.COMPLETED
                self._notify("job.completed", job)
            except Exception as exc:
                job.error = str(exc)
                job.state = JobState.FAILED
                self._notify("job.failed", job)
            return True
        if not self.persistence.claim_job(job.id, worker_id=self.worker_id,
                                          lease_seconds=self.config.lease_seconds):
            return True

        heartbeat = threading.Thread(
            target=self._heartbeat_loop,
            args=(job.id,),
            name=f"berkios-heartbeat-{job.id}",
            daemon=True,
        )
        heartbeat.start()

        try:
            handler = self.handlers.get(job.kind)
            if handler is None:
                raise KeyError(f"No handler registered for job kind: {job.kind}")

            result = handler(job)
            self.persistence.complete_job(
                job.id,
                worker_id=self.worker_id,
                result=result,
            )
        except Exception as exc:
            self.persistence.fail_job(
                job.id,
                worker_id=self.worker_id,
                error=str(exc),
            )
        finally:
            heartbeat.join(timeout=0.2)

        return True

    def run_forever(self) -> None:
        while not self._stop.is_set():
            self.run_once()


def recover_expired_jobs(
    persistence: Any,
    queue: Any,
    *,
    limit: int = 100,
) -> int:
    """
    Requeue jobs whose worker lease expired.

    The operation is intended to be safe to call periodically from more than
    one worker/process; the persistence layer must atomically transition an
    expired running job back to queued.
    """
    jobs = persistence.requeue_expired_jobs(limit=limit)
    count = 0
    for job in jobs:
        queue.enqueue(job)
        count += 1
    return count
