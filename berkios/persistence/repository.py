from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from .database import Database
from .models import PersistentApproval, PersistentEvent, PersistentJob, PersistentRun


def _job_dict(row: PersistentJob) -> dict:
    return {
        "id": row.id, "kind": row.kind, "state": row.state,
        "payload": json.loads(row.payload_json or "{}"),
        "result": json.loads(row.result_json) if row.result_json else None,
        "error": row.error, "attempts": row.attempts, "max_attempts": row.max_attempts,
        "worker_id": row.worker_id,
        "lease_until": row.lease_until.isoformat() if row.lease_until else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


class PersistenceRepository:
    def __init__(self, database: Database | None = None):
        self.database = database or Database()
        self.database.create_all()

    def upsert_run(self, run_id: str, state: str, payload: dict, project: str | None = None) -> None:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentRun, run_id)
            if row is None:
                db.add(PersistentRun(id=run_id, state=state, project=project, payload_json=json.dumps(payload, ensure_ascii=False)))
            else:
                row.state, row.project, row.payload_json = state, project, json.dumps(payload, ensure_ascii=False)
            db.commit()

    def get_run(self, run_id: str) -> dict | None:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentRun, run_id)
            if row is None: return None
            return {"id": row.id, "state": row.state, "project": row.project,
                    "payload": json.loads(row.payload_json or "{}"),
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None}

    def list_runs(self, limit: int = 200) -> list[dict]:
        with self.database.SessionLocal() as db:
            rows = db.scalars(select(PersistentRun).order_by(PersistentRun.updated_at.desc()).limit(limit)).all()
            return [{"id": r.id, "state": r.state, "project": r.project,
                     "payload": json.loads(r.payload_json or "{}"),
                     "created_at": r.created_at.isoformat() if r.created_at else None,
                     "updated_at": r.updated_at.isoformat() if r.updated_at else None} for r in rows]

    def save_approval(self, approval_id: str, decision: str, payload: dict, run_id: str | None = None, step_id: str | None = None) -> None:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentApproval, approval_id)
            if row is None:
                db.add(PersistentApproval(id=approval_id, run_id=run_id, step_id=step_id, decision=decision, payload_json=json.dumps(payload, ensure_ascii=False)))
            else:
                row.decision, row.payload_json = decision, json.dumps(payload, ensure_ascii=False)
            db.commit()

    def add_event(self, event_type: str, payload: dict, run_id: str | None = None) -> int:
        with self.database.SessionLocal() as db:
            row = PersistentEvent(run_id=run_id, event_type=event_type, payload_json=json.dumps(payload, ensure_ascii=False))
            db.add(row); db.commit(); db.refresh(row); return row.id

    def events_after(self, cursor: int = 0, run_id: str | None = None, limit: int = 200) -> list[dict]:
        with self.database.SessionLocal() as db:
            stmt = select(PersistentEvent).where(PersistentEvent.id > cursor)
            if run_id is not None: stmt = stmt.where(PersistentEvent.run_id == run_id)
            rows = db.scalars(stmt.order_by(PersistentEvent.id.asc()).limit(limit)).all()
            return [{"id": r.id, "run_id": r.run_id, "event_type": r.event_type,
                     "payload": json.loads(r.payload_json or "{}"),
                     "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]

    def create_job(self, job: dict) -> dict:
        with self.database.SessionLocal() as db:
            row = PersistentJob(id=job["id"], kind=job["kind"], state=job.get("state", "queued"),
                                payload_json=json.dumps(job.get("payload", {}), ensure_ascii=False),
                                attempts=int(job.get("attempts", 0)), max_attempts=int(job.get("max_attempts", 3)))
            db.add(row); db.commit(); db.refresh(row); return _job_dict(row)

    def get_job(self, job_id: str) -> dict | None:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentJob, job_id)
            return _job_dict(row) if row else None

    def claim_job(self, job_id: str, worker_id: str, lease_seconds: int = 60) -> dict | None:
        now = datetime.now(timezone.utc); lease = now + timedelta(seconds=lease_seconds)
        with self.database.SessionLocal() as db:
            row = db.get(PersistentJob, job_id)
            if row is None or row.state != "queued": return None
            row.state, row.worker_id, row.lease_until = "running", worker_id, lease
            row.attempts += 1; row.updated_at = now
            db.commit(); db.refresh(row); return _job_dict(row)

    def heartbeat_job(self, job_id: str, worker_id: str, lease_seconds: int = 60) -> bool:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentJob, job_id)
            if not row or row.state != "running" or row.worker_id != worker_id: return False
            row.lease_until = datetime.now(timezone.utc) + timedelta(seconds=lease_seconds)
            db.commit(); return True

    def complete_job(self, job_id: str, worker_id: str, result=None) -> bool:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentJob, job_id)
            if not row or row.state != "running" or row.worker_id != worker_id: return False
            row.state, row.result_json, row.worker_id, row.lease_until = "completed", json.dumps(result, ensure_ascii=False), None, None
            db.commit(); return True

    def fail_job(self, job_id: str, worker_id: str, error: str, retry: bool = True) -> dict | None:
        with self.database.SessionLocal() as db:
            row = db.get(PersistentJob, job_id)
            if not row or row.state != "running" or row.worker_id != worker_id: return None
            row.error, row.worker_id, row.lease_until = error, None, None
            row.state = "queued" if retry and row.attempts < row.max_attempts else "failed"
            db.commit(); db.refresh(row); return _job_dict(row)

    def recover_expired_jobs(self) -> list[dict]:
        now = datetime.now(timezone.utc); recovered = []
        with self.database.SessionLocal() as db:
            rows = db.scalars(select(PersistentJob).where(PersistentJob.state == "running", PersistentJob.lease_until < now)).all()
            for row in rows:
                row.state = "queued" if row.attempts < row.max_attempts else "failed"
                row.worker_id, row.lease_until = None, None
                recovered.append(_job_dict(row))
            db.commit()
        return recovered

    def queued_jobs(self, limit: int = 500) -> list[dict]:
        with self.database.SessionLocal() as db:
            rows = db.scalars(select(PersistentJob).where(PersistentJob.state == "queued").order_by(PersistentJob.created_at.asc()).limit(limit)).all()
            return [_job_dict(r) for r in rows]
