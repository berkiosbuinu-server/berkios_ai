from __future__ import annotations

from dataclasses import dataclass, field

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
    """Calcule les points de reprise sans exécuter d'outil."""

    def checkpoint(self, run, plan):
        completed = [
            result["step_id"]
            for result in run.results
            if result.get("success")
        ]

        blocked = [
            result["step_id"]
            for result in run.results
            if result.get("state")
            in {
                "blocked",
                "waiting_approval",
            }
        ]

        completed_set = set(completed)

        next_step = None

        for step in plan.steps:
            if step.id in completed_set:
                continue

            if all(
                dependency in completed_set
                for dependency in step.depends_on
            ):
                next_step = step.id
                break

        return ResumePoint(
            run_id=run.run_id,
            next_step_id=next_step,
            completed_steps=completed,
            blocked_steps=blocked,
            reason=(
                "reprise après approbation"
                if run.state.value == "waiting_approval"
                else "point de reprise"
            ),
        )

    def ready_steps(self, run, plan):
        completed = {
            result["step_id"]
            for result in run.results
            if result.get("success")
        }

        return [
            step
            for step in plan.steps
            if step.id not in completed
            and all(
                dependency in completed
                for dependency in step.depends_on
            )
        ]

    def prepare_resume(self, run, plan):
        for step in plan.steps:
            if step.state == ExecutionState.WAITING_APPROVAL:
                step.state = ExecutionState.READY
                step.reason = ""

        return self.ready_steps(
            run,
            plan,
        )
