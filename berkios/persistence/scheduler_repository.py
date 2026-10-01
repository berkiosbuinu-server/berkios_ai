from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScheduleRecord:
    id: str
    job_kind: str
    payload: dict[str, Any]
    next_run_at: float
    interval_seconds: float | None = None
    enabled: bool = True


class SchedulerRepository:
    """Persistence contract for the durable scheduler.

    Concrete SQL implementations can use PostgreSQL row locking / SKIP LOCKED
    to claim due schedules safely across multiple scheduler instances.
    """

    def claim_due_schedules(
        self, *, limit: int = 50, lease_seconds: int = 60
    ) -> list[ScheduleRecord]:
        raise NotImplementedError

    def mark_schedule_dispatched(self, schedule_id: str) -> None:
        raise NotImplementedError

    def release_schedule_claim(self, schedule_id: str, *, error: str) -> None:
        raise NotImplementedError
