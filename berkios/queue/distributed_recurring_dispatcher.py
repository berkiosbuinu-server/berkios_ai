from __future__ import annotations

import datetime as dt
from typing import Any

from .models import Job


class DistributedRecurringDispatcher:
    """Dispatches atomically claimed recurring occurrences.

    The persistence layer must perform the claim transactionally. The
    occurrence id is propagated as an idempotency key so duplicate delivery
    can be detected downstream.
    """

    def __init__(self, store: Any, queue: Any, cron: Any):
        self.store = store
        self.queue = queue
        self.cron = cron

    def dispatch(self, now: dt.datetime | None = None, limit: int = 50) -> int:
        now = now or dt.datetime.now(dt.timezone.utc)
        claimed = self.store.claim_due_occurrences(now=now, limit=limit)
        sent = 0

        for occurrence in claimed:
            job = Job(
                kind=occurrence.job_kind,
                payload={
                    **occurrence.payload,
                    "_recurring_schedule_id": occurrence.schedule_id,
                    "_occurrence_id": occurrence.occurrence_id,
                    "_scheduled_for": occurrence.scheduled_for.isoformat(),
                    "_idempotency_key": (
                        f"recurring:{occurrence.schedule_id}:"
                        f"{occurrence.scheduled_for.isoformat()}"
                    ),
                },
            )
            try:
                self.queue.enqueue(job)
                expression = self.cron.parse(
                    self.store.get_cron(occurrence.schedule_id)
                )
                next_run = self.cron.next_run(
                    expression, occurrence.scheduled_for
                )
                self.store.finalize_occurrence(
                    occurrence_id=occurrence.occurrence_id,
                    next_run_at=next_run,
                )
                sent += 1
            except Exception as exc:
                self.store.release_occurrence(
                    occurrence_id=occurrence.occurrence_id,
                    error=str(exc),
                )
        return sent
