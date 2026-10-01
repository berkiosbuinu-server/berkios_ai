from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid

class ErrorKind(str, Enum):
    SYNTAX="syntax"
    TYPE="type"
    IMPORT="import"
    RUNTIME="runtime"
    TEST="test"
    BUILD="build"
    LINT="lint"
    GIT="git"
    TOOL="tool"
    UNKNOWN="unknown"

class ErrorSeverity(str, Enum):
    INFO="info"
    WARNING="warning"
    ERROR="error"
    FATAL="fatal"

@dataclass
class ErrorEvent:
    message: str
    kind: ErrorKind = ErrorKind.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.ERROR
    source: str = "runtime"
    file: str | None = None
    line: int | None = None
    column: int | None = None
    code: str | None = None
    traceback: str | None = None
    command: list[str] | None = None
    stdout: str = ""
    stderr: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self):
        d = self.__dict__.copy()
        d["kind"] = self.kind.value
        d["severity"] = self.severity.value
        return d
