from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionKind(str, Enum):
    ANALYZE = "analyze"
    READ = "read"
    SEARCH = "search"
    PROPOSE_CHANGE = "propose_change"
    VERIFY = "verify"
    REPAIR = "repair"
    EXPLAIN = "explain"


@dataclass
class PlannedAction:
    id: str
    kind: ActionKind
    description: str
    capability: str | None = None
    tool: str | None = None
    target: str | None = None
    requires_approval: bool = False
    requires_verification: bool = False
    risk: str = "low"
    depends_on: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionPlan:
    request: str
    objective: str
    actions: list[PlannedAction] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    approval_required: bool = False
    verification_required: bool = True
    rationale: str = ""

    def to_dict(self):
        return {
            "request": self.request,
            "objective": self.objective,
            "actions": [
                {
                    "id": a.id,
                    "kind": a.kind.value,
                    "description": a.description,
                    "capability": a.capability,
                    "tool": a.tool,
                    "target": a.target,
                    "requires_approval": a.requires_approval,
                    "requires_verification": a.requires_verification,
                    "risk": a.risk,
                    "depends_on": a.depends_on,
                    "metadata": a.metadata,
                } for a in self.actions
            ],
            "risks": self.risks,
            "assumptions": self.assumptions,
            "approval_required": self.approval_required,
            "verification_required": self.verification_required,
            "rationale": self.rationale,
        }
