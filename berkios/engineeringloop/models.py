from dataclasses import dataclass, asdict, field

@dataclass
class EngineeringState:
    state: str
    message: str = ""
    step: int = 0
    approval_required: bool = False
    def to_dict(self): return asdict(self)

@dataclass
class EngineeringRun:
    run_id: str
    target: str
    request: str
    states: list[EngineeringState] = field(default_factory=list)
    impact: dict = field(default_factory=dict)
    explanation: dict = field(default_factory=dict)
    repair_context: dict = field(default_factory=dict)
    result: str = "pending"
    def to_dict(self):
        d=asdict(self)
        d["states"]=[s.to_dict() for s in self.states]
        return d
