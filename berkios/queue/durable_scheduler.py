from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class SchedulerConfig:
    poll_seconds: float = 2.0
    batch_size: int = 50
    lease_seconds: int = 60


class DurableScheduler:
    """PostgreSQL-backed scheduler coordinator.

    Persistence is authoritative. Multiple scheduler processes may run at once;
    the persistence layer must atomically claim due schedules so only one
    coordinator publishes a given occurrence.
    """

    def __init__(
        self,
        persistence: Any,
        queue: Any,
        job_factory: Callable[[Any], Any],
        config: SchedulerConfig | None = None,
    ):
        self.persistence = persistence
        self.queue = queue
        self.job_factory = job_factory
        self.config = config or SchedulerConfig()
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def tick(self) -> int:
        claimed = self.persistence.claim_due_schedules(
            limit=self.config.batch_size,
            lease_seconds=self.config.lease_seconds,
        )
        published = 0
        for schedule in claimed:
            try:
                job = self.job_factory(schedule)
                self.queue.enqueue(job)
                self.persistence.mark_schedule_dispatched(schedule.id)
                published += 1
            except Exception as exc:
                self.persistence.release_schedule_claim(
                    schedule.id, error=str(exc)
                )
        return published

    def run_forever(self) -> None:
        while not self._stop.is_set():
            self.tick()
            self._stop.wait(self.config.poll_seconds)


def next_run_from_interval(last_run: float, interval_seconds: float) -> float:
    return last_run + interval_seconds


def is_due(next_run: float, now: float | None = None) -> bool:
    return next_run <= (time.time() if now is None else now)
