from dataclasses import dataclass, asdict, field

@dataclass
class ContextSection:
    name: str
    content: object
    priority: float
    reason: str
    def to_dict(self): return asdict(self)

@dataclass
class AgentContext:
    request: str
    target: str | None
    sections: list[ContextSection] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    summary: str = ""
    def to_dict(self):
        d=asdict(self)
        d["sections"]=[s.to_dict() for s in self.sections]
        return d
