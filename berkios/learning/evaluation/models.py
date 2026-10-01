from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

def now(): return datetime.now(timezone.utc).isoformat()

@dataclass
class EvaluationCase:
    case_id: str
    task: str
    input_text: str
    expected: str | None = None
    tags: list[str] = field(default_factory=list)

@dataclass
class EvaluationResult:
    model_version: str
    score: float
    passed: bool
    cases_total: int
    cases_passed: int
    metrics: dict[str,float] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now)

@dataclass
class ModelRecord:
    version: str
    artifact: str | None
    status: str
    score: float
    parent_version: str | None = None
    evaluation: dict[str,Any] = field(default_factory=dict)
    metadata: dict[str,Any] = field(default_factory=dict)
    created_at: str = field(default_factory=now)
