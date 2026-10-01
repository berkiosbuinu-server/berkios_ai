from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import uuid
from datetime import datetime, timezone


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalRequest:
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str | None = None
    action_id: str | None = None
    capability: str | None = None
    title: str = ""
    description: str = ""
    risk: str = "medium"
    targets: list[str] = field(default_factory=list)
    changes: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""
    decision: ApprovalDecision = ApprovalDecision.PENDING
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    decided_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def decide(self, approved: bool):
        self.decision = (
            ApprovalDecision.APPROVED if approved
            else ApprovalDecision.REJECTED
        )
        self.decided_at = datetime.now(timezone.utc).isoformat()
        return self

    def to_dict(self):
        return {
            "approval_id": self.approval_id,
            "run_id": self.run_id,
            "action_id": self.action_id,
            "capability": self.capability,
            "title": self.title,
            "description": self.description,
            "risk": self.risk,
            "targets": self.targets,
            "changes": self.changes,
            "reason": self.reason,
            "decision": self.decision.value,
            "created_at": self.created_at,
            "decided_at": self.decided_at,
            "metadata": self.metadata,
        }
