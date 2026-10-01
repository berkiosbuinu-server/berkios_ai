from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any


@dataclass
class ClaimedOccurrence:
    schedule_id: str
    occurrence_id: str
    job_kind: str
    payload: dict[str, Any]
    scheduled_for: dt.datetime


class RecurringClaimStore:
    """Persistence contract for atomic recurring-occurrence claims."""

    def claim_due_occurrences(
        self,
        *,
        now: dt.datetime,
        limit: int = 50,
        lease_seconds: int = 60,
    ) -> list[ClaimedOccurrence]:
        raise NotImplementedError

    def finalize_occurrence(
        self,
        *,
        occurrence_id: str,
        next_run_at: dt.datetime,
    ) -> None:
        raise NotImplementedError

    def release_occurrence(
        self,
        *,
        occurrence_id: str,
        error: str,
    ) -> None:
        raise NotImplementedError
