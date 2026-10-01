from dataclasses import dataclass, asdict

@dataclass
class VerificationFinding:
    target: str
    status: str
    severity: str
    message: str
    related_change: str = ""
    def to_dict(self): return asdict(self)

@dataclass
class VerificationReport:
    change_target: str
    passed: bool
    findings: list[VerificationFinding]
    verified_targets: list[str]
    skipped_targets: list[str]
    summary: str
    next_action: str
    def to_dict(self):
        d=asdict(self)
        d["findings"]=[x.to_dict() for x in self.findings]
        return d
