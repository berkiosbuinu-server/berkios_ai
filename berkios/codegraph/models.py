from dataclasses import dataclass, asdict

@dataclass
class GraphPath:
    nodes: list[str]
    relation: str
    description: str = ""
    def to_dict(self): return asdict(self)

@dataclass
class GraphImpact:
    target: str
    direct_dependents: list[str]
    indirect_dependents: list[str]
    dependencies: list[str]
    paths: list[GraphPath]
    risk_level: str
    explanation: str
    def to_dict(self):
        d=asdict(self)
        d["paths"]=[p.to_dict() for p in self.paths]
        return d
