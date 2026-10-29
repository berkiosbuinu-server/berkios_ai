from __future__ import annotations

from .models import (
    ActionKind,
    ActionPlan,
    PlannedAction,
)


class ActionPlanner:
    """
    Transforme une décision structurée en plan exécutable.

    Le planner ne lance jamais directement un outil.
    """

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

        # -----------------------------------------------------
        # Analyse initiale
        # -----------------------------------------------------

        steps.append(
            PlannedAction(
                id="a1",
                kind=ActionKind.ANALYZE,
                description="Analyser la demande et le contexte pertinent",
                capability="context.read",
                target=target,
                requires_verification=False,
            )
        )

        # -----------------------------------------------------
        # Modification / réparation
        # -----------------------------------------------------

        if action in {
            "analyze_and_propose_change",
            "analyze_and_propose_repair",
            "repair",
            "propose_change",
            "change",
        }:
            steps.append(
                PlannedAction(
                    id="a2",
                    kind=ActionKind.READ,
                    description=(
                        "Lire les fichiers et symboles nécessaires "
                        "avant modification"
                    ),
                    capability="filesystem.read",
                    target=target,
                    depends_on=["a1"],
                )
            )

            steps.append(
                PlannedAction(
                    id="a3",
                    kind=ActionKind.PROPOSE_CHANGE,
                    description=(
                        "Construire une proposition de modification "
                        "minimale"
                    ),
                    capability="changes.propose",
                    target=target,
                    requires_approval=True,
                    requires_verification=True,
                    risk="medium",
                    depends_on=["a2"],
                )
            )

            steps.append(
                PlannedAction(
                    id="a4",
                    kind=ActionKind.VERIFY,
                    description=(
                        "Vérifier la modification et analyser "
                        "les erreurs éventuelles"
                    ),
                    capability="verification.run",
                    target=target,
                    requires_verification=True,
                    depends_on=["a3"],
                )
            )

            risks.append(
                "La modification nécessite une approbation explicite."
            )

        # -----------------------------------------------------
        # Explication
        # -----------------------------------------------------

        elif action == "explain":
            steps.append(
                PlannedAction(
                    id="a2",
                    kind=ActionKind.EXPLAIN,
                    description=(
                        "Produire une explication fondée "
                        "sur le contexte du projet"
                    ),
                    capability="code.explain",
                    target=target,
                    depends_on=["a1"],
                )
            )

        # -----------------------------------------------------
        # Recherche
        # -----------------------------------------------------

        elif action in {
            "search",
            "inspect",
            "find",
            "lookup",
        }:
            steps.append(
                PlannedAction(
                    id="a2",
                    kind=ActionKind.SEARCH,
                    description=(
                        "Rechercher les informations nécessaires "
                        "dans le projet"
                    ),
                    capability="filesystem.search",
                    target=context.get("query") or target,
                    depends_on=["a1"],
                    metadata={
                        "args": {
                            "query": context.get("query")
                            or request,
                        }
                    },
                )
            )

        # -----------------------------------------------------
        # Analyse par défaut
        # -----------------------------------------------------

        else:
            steps.append(
                PlannedAction(
                    id="a2",
                    kind=ActionKind.SEARCH,
                    description=(
                        "Rechercher les informations nécessaires "
                        "avant toute action"
                    ),
                    capability="filesystem.search",
                    target=context.get("query") or target,
                    depends_on=["a1"],
                    metadata={
                        "args": {
                            "query": context.get("query")
                            or request,
                        }
                    },
                )
            )

        rationale = (
            getattr(decision, "rationale", "")
            or "Plan dérivé de la décision structurée."
        )

        return ActionPlan(
            request=request,
            objective=(
                getattr(decision, "objective", "")
                or request
            ),
            actions=steps,
            risks=risks,
            assumptions=assumptions,
            approval_required=any(
                x.requires_approval
                for x in steps
            ),
            verification_required=any(
                x.requires_verification
                for x in steps
            ),
            rationale=rationale,
        )
