from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from .models import TeacherSample, TeacherSession


class TeacherDataBuilder:
    """Normalize provider/teacher outputs into Codix learning candidates.

    The builder deliberately stops before training. Every candidate still has
    to pass the explicit consent, human review, curation and evaluation stages.
    """

    def __init__(self, root: str | Path = ".berkios/teacher_data"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _id(self, provider: str, task: str, output: str) -> str:
        raw = f"{provider}\0{task}\0{output}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:20]

    def normalize(
        self,
        *,
        provider: str,
        model: str | None,
        task: str,
        input_context: str,
        output: str,
        provenance: dict[str, Any] | None = None,
        tests: list[str] | None = None,
    ) -> TeacherSample:
        return TeacherSample(
            sample_id=self._id(provider, task, output),
            teacher_provider=provider,
            teacher_model=model,
            task=task,
            input_context=input_context,
            teacher_output=output,
            provenance=provenance or {},
            tests=tests or [],
        )

    def compare(
        self,
        *,
        task: str,
        samples: list[TeacherSample],
    ) -> TeacherSession:
        providers = list(dict.fromkeys(s.teacher_provider for s in samples))
        session_id = self._id("multi-teacher", task, "|".join(s.sample_id for s in samples))
        session = TeacherSession(
            session_id=session_id,
            task=task,
            providers=providers,
            samples=list(samples),
        )
        session.consensus = self._consensus(samples)
        return session

    def _consensus(self, samples: list[TeacherSample]) -> str | None:
        if not samples:
            return None
        # Conservative consensus: only return an identical output.
        outputs = {s.teacher_output for s in samples}
        return next(iter(outputs)) if len(outputs) == 1 else None

    def save(self, sample: TeacherSample) -> Path:
        path = self.root / f"{sample.sample_id}.json"
        path.write_text(
            json.dumps(sample.__dict__, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def save_session(self, session: TeacherSession) -> Path:
        path = self.root / f"session_{session.session_id}.json"
        payload = {
            "session_id": session.session_id,
            "task": session.task,
            "providers": session.providers,
            "consensus": session.consensus,
            "created_at": session.created_at,
            "samples": [s.__dict__ for s in session.samples],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
