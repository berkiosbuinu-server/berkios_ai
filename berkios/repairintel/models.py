from dataclasses import dataclass, asdict

@dataclass
class RepairContext:
    change_target: str
    error_message: str
    error_kind: str
    affected_files: list[str]
    evidence: list[str]
    historical_hints: list[str]
    constraints: list[str]
    def to_dict(self): return asdict(self)

@dataclass
class RepairPlan:
    context: RepairContext
    diagnosis: str
    likely_causes: list[str]
    repair_steps: list[str]
    verification_steps: list[str]
    approval_required: bool = True
    def to_dict(self):
        d=asdict(self)
        d["context"]=self.context.to_dict()
        return d
