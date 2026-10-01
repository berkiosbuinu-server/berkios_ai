from __future__ import annotations

import datetime as dt
import json
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class RecurringJobRecord:
    id: str
    job_kind: str
    payload: dict[str, Any]
    cron: str
    timezone: str = "UTC"
    enabled: bool = True
    next_run_at: dt.datetime | None = None
    last_run_at: dt.datetime | None = None


class RecurringJobStore:
    """PostgreSQL repository for persistent recurring jobs.

    The implementation is deliberately DB-driver agnostic and expects a
    connection object exposing execute/commit semantics. Production callers
    can adapt it to SQLAlchemy or psycopg.
    """

    CREATE_SQL = """
    CREATE TABLE IF NOT EXISTS berkios_recurring_jobs (
        id TEXT PRIMARY KEY,
        job_kind TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        cron TEXT NOT NULL,
        timezone TEXT NOT NULL DEFAULT 'UTC',
        enabled BOOLEAN NOT NULL DEFAULT TRUE,
        next_run_at TIMESTAMPTZ,
        last_run_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """

    def __init__(self, connection: Any):
        self.connection = connection

    def initialize(self) -> None:
        self.connection.execute(self.CREATE_SQL)
        self.connection.commit()

    def upsert(self, record: RecurringJobRecord) -> RecurringJobRecord:
        if not record.id:
            record.id = uuid.uuid4().hex
        self.connection.execute(
            """
            INSERT INTO berkios_recurring_jobs
              (id, job_kind, payload_json, cron, timezone, enabled,
               next_run_at, last_run_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
              job_kind=EXCLUDED.job_kind,
              payload_json=EXCLUDED.payload_json,
              cron=EXCLUDED.cron,
              timezone=EXCLUDED.timezone,
              enabled=EXCLUDED.enabled,
              next_run_at=EXCLUDED.next_run_at,
              last_run_at=EXCLUDED.last_run_at,
              updated_at=NOW()
            """,
            (
                record.id, record.job_kind, json.dumps(record.payload),
                record.cron, record.timezone, record.enabled,
                record.next_run_at, record.last_run_at,
            ),
        )
        self.connection.commit()
        return record

    def set_enabled(self, job_id: str, enabled: bool) -> None:
        self.connection.execute(
            """
            UPDATE berkios_recurring_jobs
               SET enabled=%s, updated_at=NOW()
             WHERE id=%s
            """,
            (enabled, job_id),
        )
        self.connection.commit()

    def list_enabled(self) -> list[RecurringJobRecord]:
        cur = self.connection.execute(
            """
            SELECT id, job_kind, payload_json, cron, timezone, enabled,
                   next_run_at, last_run_at
              FROM berkios_recurring_jobs
             WHERE enabled=TRUE
             ORDER BY next_run_at NULLS FIRST
            """
        )
        rows = cur.fetchall()
        return [
            RecurringJobRecord(
                id=r[0], job_kind=r[1], payload=json.loads(r[2]),
                cron=r[3], timezone=r[4], enabled=r[5],
                next_run_at=r[6], last_run_at=r[7],
            )
            for r in rows
        ]

    def mark_occurrence(
        self, job_id: str, *, last_run_at: dt.datetime, next_run_at: dt.datetime
    ) -> None:
        self.connection.execute(
            """
            UPDATE berkios_recurring_jobs
               SET last_run_at=%s, next_run_at=%s, updated_at=NOW()
             WHERE id=%s
            """,
            (last_run_at, next_run_at, job_id),
        )
        self.connection.commit()
