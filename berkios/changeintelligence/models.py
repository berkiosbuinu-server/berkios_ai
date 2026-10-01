from dataclasses import dataclass, asdict

@dataclass
class VerificationTarget:
    target: str
    reason: str
    priority: str = "normal"
    def to_dict(self): return asdict(self)

@dataclass
class ChangeImpactPlan:
    requested_target: str
    affected_files: list[str]
    affected_symbols: list[str]
    direct_impact: list[str]
    indirect_impact: list[str]
    risks: list[str]
    verification_targets: list[VerificationTarget]
    steps: list[str]
    approval_required: bool = True
    def to_dict(self):
        d=asdict(self)
        d["verification_targets"]=[x.to_dict() for x in self.verification_targets]
        return d
