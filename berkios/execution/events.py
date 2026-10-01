from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExecutionEvent:
    event: str
    step_id: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "event": self.event,
            "step_id": self.step_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }
