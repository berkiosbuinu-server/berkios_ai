from __future__ import annotations

import datetime as dt
from typing import Any

from .recurring import CronEngine
from .models import Job


class RecurringDispatcher:
    """Turns due persistent recurring definitions into normal queue jobs."""

    def __init__(self, store: Any, queue: Any, cron: CronEngine | None = None):
        self.store = store
        self.queue = queue
        self.cron = cron or CronEngine()

    def dispatch_due(self, now: dt.datetime | None = None) -> int:
        now = now or dt.datetime.now(dt.timezone.utc)
        dispatched = 0

        for record in self.store.list_enabled():
            expression = self.cron.parse(record.cron)
            next_run = record.next_run_at

            if next_run is None:
                next_run = self.cron.next_run(expression, now - dt.timedelta(minutes=1))
                self.store.mark_occurrence(
                    record.id, last_run_at=now, next_run_at=next_run
                )
                continue

            if next_run > now:
                continue

            job = Job(
                kind=record.job_kind,
                payload={
                    **record.payload,
                    "_recurring_job_id": record.id,
                    "_scheduled_for": next_run.isoformat(),
                },
            )
            self.queue.enqueue(job)

            following = self.cron.next_run(expression, next_run)
            self.store.mark_occurrence(
                record.id, last_run_at=next_run, next_run_at=following
            )
            dispatched += 1

        return dispatched
