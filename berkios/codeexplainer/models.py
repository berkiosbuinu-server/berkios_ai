from dataclasses import dataclass, asdict

@dataclass
class CodeConnection:
    source: str
    target: str
    kind: str
    description: str = ""
    def to_dict(self): return asdict(self)

@dataclass
class CodeExplanation:
    target: str
    language: str
    summary: str
    purpose: str
    usage: list[str]
    inputs: list[str]
    outputs: list[str]
    dependencies: list[str]
    symbols: list[str]
    connections: list[CodeConnection]
    flow: list[str]
    risks: list[str]
    suggestions: list[str]
    confidence: float = 0.0
    def to_dict(self):
        d=asdict(self); d["connections"]=[x.to_dict() for x in self.connections]; return d
