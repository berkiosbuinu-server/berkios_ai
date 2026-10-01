from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RecurringJob:
    id: str
    job_kind: str
    payload: dict[str, Any]
    cron: str
    timezone: str = "UTC"
    enabled: bool = True


class RecurringJobRepository:
    """Persistence contract for recurring jobs."""

    def create(self, job: RecurringJob) -> None:
        raise NotImplementedError

    def get(self, job_id: str) -> RecurringJob | None:
        raise NotImplementedError

    def disable(self, job_id: str) -> None:
        raise NotImplementedError

    def list_enabled(self) -> list[RecurringJob]:
        raise NotImplementedError

    def update_next_run(self, job_id: str, next_run_at: float) -> None:
        raise NotImplementedError
