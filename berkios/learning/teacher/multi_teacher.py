from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from .models import TeacherSample, TeacherSession


@dataclass
class TeacherComparison:
    task: str
    samples: list[TeacherSample]
    agreement_groups: list[list[str]] = field(default_factory=list)
    selected_sample_id: str | None = None
    synthesis: str | None = None
    rationale: str = ""


class MultiTeacherEngine:
    """Compare independent teacher outputs without silently training Codix.

    Selection is intentionally conservative:
    - identical outputs form an agreement group;
    - if there is a unique largest group, it may be selected as a candidate;
    - divergent outputs are never silently merged;
    - synthesis is explicit and remains a review candidate.
    """

    def compare(self, task: str, samples: list[TeacherSample]) -> TeacherComparison:
        groups: dict[str, list[str]] = {}
        for sample in samples:
            key = sha256(sample.teacher_output.strip().encode("utf-8")).hexdigest()
            groups.setdefault(key, []).append(sample.sample_id)

        ordered = sorted(groups.values(), key=len, reverse=True)
        result = TeacherComparison(task=task, samples=list(samples),
                                   agreement_groups=ordered)

        if len(ordered) == 1 and ordered:
            result.selected_sample_id = ordered[0][0]
            result.rationale = "All teacher outputs are identical."
        elif len(ordered) > 1 and len(ordered[0]) > len(ordered[1]):
            result.selected_sample_id = ordered[0][0]
            result.rationale = "A unique largest agreement group exists; human review remains required."
        else:
            result.rationale = "No unique consensus; human review or explicit synthesis is required."
        return result

    def synthesize(
        self,
        comparison: TeacherComparison,
        *,
        synthesis: str,
        rationale: str,
    ) -> TeacherComparison:
        comparison.synthesis = synthesis
        comparison.rationale = rationale
        return comparison

    def to_candidate(self, comparison: TeacherComparison) -> TeacherSample | None:
        if not comparison.synthesis:
            return None
        if not comparison.samples:
            return None

        first = comparison.samples[0]
        return TeacherSample(
            sample_id=sha256(
                f"multi-teacher\0{comparison.task}\0{comparison.synthesis}".encode("utf-8")
            ).hexdigest()[:20],
            teacher_provider="multi-teacher",
            teacher_model=None,
            task=comparison.task,
            input_context=first.input_context,
            teacher_output=comparison.synthesis,
            provenance={
                "kind": "multi_teacher_synthesis",
                "source_sample_ids": [s.sample_id for s in comparison.samples],
                "providers": [s.teacher_provider for s in comparison.samples],
                "rationale": comparison.rationale,
            },
            tests=list(dict.fromkeys(t for s in comparison.samples for t in s.tests)),
            evaluation={"requires_human_review": True},
            consent_required=True,
        )
