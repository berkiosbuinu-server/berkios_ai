from __future__ import annotations

from berkios.learning.teacher import MultiTeacherEngine, TeacherSample


class RuntimeCodixMultiTeacher:
    """Runtime facade for multi-teacher Codix candidate construction."""

    def __init__(self):
        self.engine = MultiTeacherEngine()

    def compare(self, task: str, samples: list[TeacherSample]):
        return self.engine.compare(task, samples)

    def synthesize(self, comparison, synthesis: str, rationale: str):
        return self.engine.synthesize(
            comparison,
            synthesis=synthesis,
            rationale=rationale,
        )

    def candidate(self, comparison):
        return self.engine.to_candidate(comparison)
