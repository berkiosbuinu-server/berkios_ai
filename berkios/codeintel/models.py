from dataclasses import dataclass, field

@dataclass
class Symbol:
    name: str
    kind: str
    file: str
    line: int
    column: int = 0
    parent: str | None = None
    def to_dict(self): return self.__dict__.copy()

@dataclass
class FileAnalysis:
    path: str
    language: str
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    lines: int = 0
    def to_dict(self):
        return {"path": self.path, "language": self.language,
                "symbols": [s.to_dict() for s in self.symbols],
                "imports": self.imports, "lines": self.lines}
