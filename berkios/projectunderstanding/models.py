from dataclasses import dataclass, asdict

@dataclass
class ProjectComponent:
    name: str
    path: str
    kind: str
    role: str
    dependencies: list[str]
    symbols: list[str]
    def to_dict(self): return asdict(self)

@dataclass
class ProjectUnderstanding:
    project_name: str
    languages: list[str]
    components: list[ProjectComponent]
    entry_points: list[str]
    architecture: list[str]
    flows: list[str]
    external_dependencies: list[str]
    risks: list[str]
    summary: str
    confidence: float
    def to_dict(self):
        d=asdict(self)
        d["components"]=[x.to_dict() for x in self.components]
        return d
