from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class JobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = ""
    state: JobState = JobState.QUEUED
    attempts: int = 0
    max_attempts: int = 3
    worker_id: str | None = None
    lease_expires_at: float | None = None
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
            "state": self.state.value,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "worker_id": self.worker_id,
            "lease_expires_at": self.lease_expires_at,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Job":
        return cls(
            id=data.get("id", ""),
            kind=data["kind"],
            payload=data.get("payload", {}),
            state=JobState(data.get("state", JobState.QUEUED.value)),
            attempts=int(data.get("attempts", 0)),
            max_attempts=int(data.get("max_attempts", 3)),
            worker_id=data.get("worker_id"),
            lease_expires_at=data.get("lease_expires_at"),
            result=data.get("result"),
            error=data.get("error"),
        )
