from __future__ import annotations
from .models import ExecutionPlan, ExecutionStep, ExecutionState


class ExecutionPlanner:
    """Construit une séquence exécutable sans exécuter d'outil."""

    def build(self, action_plan, capability_matches=None):
        capability_matches = capability_matches or []
        by_action = {m.action_id: m for m in capability_matches}
        steps = []
        blocked = []

        for action in action_plan.actions:
            match = by_action.get(action.id)
            available = True if match is None else match.available

            if not available:
                state = ExecutionState.BLOCKED
                reason = "capacité indisponible"
                blocked.append(f"{action.id}: {reason}")
            elif action.requires_approval:
                state = ExecutionState.WAITING_APPROVAL
                reason = "approbation explicite requise"
            else:
                state = ExecutionState.READY
                reason = "prêt à être exécuté"

            steps.append(ExecutionStep(
                id=f"x_{action.id}",
                action_id=action.id,
                capability=action.capability,
                state=state,
                depends_on=[f"x_{d}" for d in action.depends_on],
                requires_approval=action.requires_approval,
                requires_verification=action.requires_verification,
                tool=action.tool,
                target=action.target,
                reason=reason,
                metadata=dict(action.metadata),
            ))

        # Une étape ne peut devenir READY que si toutes ses dépendances sont
        # satisfaites. On garde WAITING_APPROVAL explicite pour les changements.
        states = {s.id: s.state for s in steps}
        for step in steps:
            if step.state == ExecutionState.BLOCKED:
                continue
            if any(states.get(dep) in {
                ExecutionState.BLOCKED,
                ExecutionState.WAITING_APPROVAL
            } for dep in step.depends_on):
                step.state = ExecutionState.BLOCKED
                step.reason = "dépendance non résolue"
                blocked.append(f"{step.id}: dépendance non résolue")

        return ExecutionPlan(
            request=action_plan.request,
            steps=steps,
            blocked_reasons=blocked,
        )
