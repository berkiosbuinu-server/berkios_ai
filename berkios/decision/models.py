from dataclasses import dataclass, asdict, field

@dataclass
class DecisionAction:
    action: str
    reason: str
    prerequisites: list[str] = field(default_factory=list)
    approval_required: bool = True
    verification_required: bool = True
    def to_dict(self): return asdict(self)

@dataclass
class Decision:
    request: str
    objective: str
    interpretation: str
    evidence: list[str]
    constraints: list[str]
    actions: list[DecisionAction]
    selected_action: str | None
    rationale: str
    uncertainty: list[str]
    def to_dict(self):
        d=asdict(self)
        d["actions"]=[a.to_dict() for a in self.actions]
        return d
