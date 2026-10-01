from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any
import uuid


class RunState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionRun:
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request: str = ""
    state: RunState = RunState.CREATED
    results: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def emit(self, event: str, **data):
        item = {
            "event": event,
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self.events.append(item)
        return item

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "request": self.request,
            "state": self.state.value,
            "results": self.results,
            "events": self.events,
            "created_at": self.created_at,
        }
