from __future__ import annotations

import heapq
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class ScheduledJob:
    run_at: float
    sequence: int
    job: Any = field(compare=False)


class JobScheduler:
    """In-process scheduler for delayed jobs.

    Persistence remains the source of truth. This scheduler only decides
    when a queued job becomes eligible for enqueueing.
    """

    def __init__(self, queue: Any, persistence: Any):
        self.queue = queue
        self.persistence = persistence
        self._items: list[ScheduledJob] = []
        self._cv = threading.Condition()
        self._seq = 0
        self._stop = False
        self._thread = threading.Thread(
            target=self._loop, name="berkios-scheduler", daemon=True
        )

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        with self._cv:
            self._stop = True
            self._cv.notify_all()

    def schedule(self, job: Any, run_at: float | None = None) -> str:
        if not getattr(job, "id", None):
            job.id = uuid.uuid4().hex
        when = time.time() if run_at is None else float(run_at)
        with self._cv:
            self._seq += 1
            heapq.heappush(self._items, ScheduledJob(when, self._seq, job))
            self._cv.notify_all()
        return job.id

    def _loop(self) -> None:
        while True:
            with self._cv:
                if self._stop:
                    return
                if not self._items:
                    self._cv.wait(timeout=1.0)
                    continue
                item = self._items[0]
                delay = item.run_at - time.time()
                if delay > 0:
                    self._cv.wait(timeout=delay)
                    continue
                heapq.heappop(self._items)

            try:
                self.queue.enqueue(item.job)
            except Exception:
                # Leave durable recovery/retry to the persistence layer.
                continue
