from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TeacherSample:
    """A provider-generated candidate example for Codix learning.

    This is not training data until it passes the normal consent/review/curation
    pipeline. Private project material must not be treated as reusable training
    data merely because a provider generated an answer from it.
    """
    sample_id: str
    teacher_provider: str
    teacher_model: str | None
    task: str
    input_context: str
    teacher_output: str
    provenance: dict[str, Any] = field(default_factory=dict)
    tests: list[str] = field(default_factory=list)
    evaluation: dict[str, Any] = field(default_factory=dict)
    consent_required: bool = True
    created_at: str = field(default_factory=utc_now)


@dataclass
class TeacherSession:
    session_id: str
    task: str
    providers: list[str]
    samples: list[TeacherSample] = field(default_factory=list)
    consensus: str | None = None
    created_at: str = field(default_factory=utc_now)

    def add(self, sample: TeacherSample) -> None:
        self.samples.append(sample)
