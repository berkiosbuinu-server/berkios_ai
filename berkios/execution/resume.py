from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from .models import ExecutionState


@dataclass
class ResumePoint:
    run_id: str
    next_step_id: str | None
    completed_steps: list[str] = field(default_factory=list)
    blocked_steps: list[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "next_step_id": self.next_step_id,
            "completed_steps": self.completed_steps,
            "blocked_steps": self.blocked_steps,
            "reason": self.reason,
        }


class ExecutionResumer:
    """Calcule et reprend un run sans rejouer les étapes terminées."""

    def checkpoint(self, run, plan) -> ResumePoint:
        completed = []
        blocked = []
        for result in run.results:
            if result.get("success"):
                completed.append(result["step_id"])
            elif result.get("state") in {
                "blocked", "waiting_approval"
            }:
                blocked.append(result["step_id"])

        next_step = None
        for step in plan.steps:
            if step.id not in completed:
                next_step = step.id
                break

        return ResumePoint(
            run_id=run.run_id,
            next_step_id=next_step,
            completed_steps=completed,
            blocked_steps=blocked,
            reason="reprise après checkpoint",
        )

    def ready_steps(self, run, plan):
        completed = {
            r["step_id"] for r in run.results if r.get("success")
        }
        return [
            step for step in plan.steps
            if step.id not in completed
            and step.state == ExecutionState.READY
            and all(dep in completed for dep in step.depends_on)
        ]
