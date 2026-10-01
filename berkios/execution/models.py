from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionState(str, Enum):
    BLOCKED = "blocked"
    READY = "ready"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExecutionStep:
    id: str
    action_id: str
    capability: str | None
    state: ExecutionState = ExecutionState.BLOCKED
    depends_on: list[str] = field(default_factory=list)
    requires_approval: bool = False
    requires_verification: bool = False
    tool: str | None = None
    target: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    request: str
    steps: list[ExecutionStep] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "request": self.request,
            "steps": [
                {
                    "id": s.id,
                    "action_id": s.action_id,
                    "capability": s.capability,
                    "state": s.state.value,
                    "depends_on": s.depends_on,
                    "requires_approval": s.requires_approval,
                    "requires_verification": s.requires_verification,
                    "tool": s.tool,
                    "target": s.target,
                    "reason": s.reason,
                    "metadata": s.metadata,
                } for s in self.steps
            ],
            "blocked_reasons": self.blocked_reasons,
        }
