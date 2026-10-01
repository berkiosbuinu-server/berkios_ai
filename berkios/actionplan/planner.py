from __future__ import annotations
import re
from .models import ActionKind, ActionPlan, PlannedAction


class ActionPlanner:
    """Transforme une Decision en plan exécutable, sans exécuter les actions."""

    def plan(self, decision, request: str, context=None) -> ActionPlan:
        context = context or {}
        action = getattr(decision, "action", None)
        if hasattr(action, "value"):
            action = action.value
        action = action or "analyze"

        target = context.get("active_file")
        steps = []
        risks = []
        assumptions = []

        steps.append(PlannedAction(
            id="a1",
            kind=ActionKind.ANALYZE,
            description="Analyser la demande et le contexte pertinent",
            capability="context.read",
            target=target,
            requires_verification=False,
        ))

        if action in {"analyze_and_propose_change", "analyze_and_propose_repair",
                      "repair", "propose_change", "change"}:
            steps.append(PlannedAction(
                id="a2",
                kind=ActionKind.READ,
                description="Lire les fichiers et symboles nécessaires avant modification",
                capability="filesystem.read",
                target=target,
                depends_on=["a1"],
            ))
            steps.append(PlannedAction(
                id="a3",
                kind=ActionKind.PROPOSE_CHANGE,
                description="Construire une proposition de modification minimale",
                capability="changes.propose",
                target=target,
                requires_approval=True,
                requires_verification=True,
                risk="medium",
                depends_on=["a2"],
            ))
            steps.append(PlannedAction(
                id="a4",
                kind=ActionKind.VERIFY,
                description="Vérifier la modification et analyser les erreurs éventuelles",
                capability="verification.run",
                target=target,
                requires_verification=True,
                depends_on=["a3"],
            ))
            risks.append("La modification nécessite une approbation explicite.")
        elif action == "explain":
            steps.append(PlannedAction(
                id="a2",
                kind=ActionKind.EXPLAIN,
                description="Produire une explication fondée sur le contexte du projet",
                capability="code.explain",
                target=target,
                depends_on=["a1"],
            ))
        else:
            steps.append(PlannedAction(
                id="a2",
                kind=ActionKind.SEARCH,
                description="Inspecter les informations nécessaires avant toute action",
                capability="project.search",
                target=target,
                depends_on=["a1"],
            ))

        rationale = getattr(decision, "rationale", "") or "Plan dérivé de la décision structurée."
        return ActionPlan(
            request=request,
            objective=getattr(decision, "objective", "") or request,
            actions=steps,
            risks=risks,
            assumptions=assumptions,
            approval_required=any(x.requires_approval for x in steps),
            verification_required=any(x.requires_verification for x in steps),
            rationale=rationale,
        )
