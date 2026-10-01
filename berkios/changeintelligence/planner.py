from pathlib import Path
from berkios.codegraph import CodeGraphIntelligence
from .models import ChangeImpactPlan, VerificationTarget

class ChangeImpactPlanner:
    """Prépare une modification en reliant impact, risques et vérification."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()
        self.graph=CodeGraphIntelligence(self.workspace)

    def plan(self, target, change_description=""):
        impact=self.graph.impact(target)
        affected=sorted(set(
            impact.direct_dependents + impact.indirect_dependents + [target]
        ))

        risks=[]
        if impact.risk_level=="high":
            risks.append("Impact en cascade important : plusieurs composants doivent être vérifiés.")
        elif impact.risk_level=="medium":
            risks.append("Des composants dépendants doivent être vérifiés.")
        if change_description:
            risks.append(f"Changement demandé : {change_description}")

        checks=[]
        checks.append(VerificationTarget(target, "Vérifier directement le composant modifié.", "high"))
        for f in impact.direct_dependents[:10]:
            checks.append(VerificationTarget(f, "Dépendance directe du composant modifié.", "high"))
        for f in impact.indirect_dependents[:10]:
            checks.append(VerificationTarget(f, "Dépendance indirecte détectée.", "normal"))

        steps=[
            "Analyser le contexte et les relations du composant.",
            "Présenter l'impact avant modification.",
            "Proposer la modification.",
            "Demander l'approbation si une écriture est nécessaire.",
            "Appliquer la modification approuvée.",
            "Exécuter les vérifications prioritaires.",
            "Analyser les nouveaux diagnostics et erreurs.",
        ]

        return ChangeImpactPlan(
            requested_target=target,
            affected_files=affected,
            affected_symbols=[],
            direct_impact=impact.direct_dependents,
            indirect_impact=impact.indirect_dependents,
            risks=risks,
            verification_targets=checks,
            steps=steps,
            approval_required=True,
        )
