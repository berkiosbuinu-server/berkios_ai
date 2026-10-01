from dataclasses import dataclass, field
from typing import Any

@dataclass
class LSPLocation:
    uri: str
    line: int
    character: int = 0

@dataclass
class LSPDiagnostic:
    message: str
    severity: int | None = None
    location: LSPLocation | None = None
    source: str | None = None
    code: Any = None

@dataclass
class LSPResult:
    operation: str
    items: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[LSPDiagnostic] = field(default_factory=list)
    raw: Any = None
