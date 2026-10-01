from __future__ import annotations

from pathlib import Path
from berkios.learning.teacher import TeacherDataBuilder, TeacherSample, TeacherSession


class RuntimeCodixTeacher:
    """Runtime facade for provider-neutral Codix teacher data generation."""

    def __init__(self, root: str | Path = ".berkios/teacher_data"):
        self.builder = TeacherDataBuilder(root)

    def candidate(
        self,
        *,
        provider: str,
        model: str | None,
        task: str,
        input_context: str,
        output: str,
        provenance: dict | None = None,
        tests: list[str] | None = None,
    ) -> TeacherSample:
        return self.builder.normalize(
            provider=provider,
            model=model,
            task=task,
            input_context=input_context,
            output=output,
            provenance=provenance,
            tests=tests,
        )

    def compare(self, *, task: str, samples: list[TeacherSample]) -> TeacherSession:
        return self.builder.compare(task=task, samples=samples)
