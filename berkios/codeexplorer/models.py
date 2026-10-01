from dataclasses import dataclass, asdict

@dataclass
class CodeRelation:
    source: str
    target: str
    kind: str
    explanation: str = ""
    file: str | None = None
    line: int | None = None

    def to_dict(self):
        return asdict(self)

@dataclass
class CodeExplorerReport:
    target: str
    definition: str | None
    used_by: list[CodeRelation]
    uses: list[CodeRelation]
    imports: list[CodeRelation]
    imported_by: list[CodeRelation]
    related_files: list[str]
    impact: list[str]
    flow: list[str]
    why: str
    usage_examples: list[str]

    def to_dict(self):
        d=asdict(self)
        for k in ("used_by","uses","imports","imported_by"):
            d[k]=[x.to_dict() for x in getattr(self,k)]
        return d
