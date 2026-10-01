from pathlib import Path
from .models import RepairContext, RepairPlan

class RepairIntelligence:
    """Prépare des réparations à partir d'une erreur vérifiée et de son contexte."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()

    def prepare(self, change_target, error_message, error_kind="unknown",
                affected_files=None, evidence=None, historical_hints=None):
        affected_files=list(affected_files or [])
        evidence=list(evidence or [])
        historical_hints=list(historical_hints or [])

        constraints=[
            "Ne pas appliquer automatiquement la réparation.",
            "Conserver les permissions et l'approbation du runtime.",
            "Re-vérifier les cibles affectées après la réparation.",
        ]

        context=RepairContext(
            change_target=change_target,
            error_message=error_message,
            error_kind=error_kind,
            affected_files=affected_files,
            evidence=evidence,
            historical_hints=historical_hints,
            constraints=constraints,
        )

        causes=[]
        if error_kind=="syntax":
            causes.append("La modification a probablement introduit une syntaxe invalide.")
        elif error_kind=="import":
            causes.append("Une dépendance ou un chemin d'import peut être incorrect.")
        elif error_kind=="type":
            causes.append("Les types attendus et produits peuvent être incompatibles.")
        elif error_kind=="test":
            causes.append("Le comportement attendu par un test n'est plus respecté.")
        elif error_kind=="runtime":
            causes.append("Le nouveau chemin d'exécution rencontre une erreur à l'exécution.")
        else:
            causes.append("Le diagnostic doit être confirmé à partir des traces et du code affecté.")

        steps=[
            "Examiner l'erreur et ses preuves.",
            "Comparer l'erreur avec le changement demandé.",
            "Inspecter les fichiers et symboles affectés.",
            "Consulter les corrections historiques pertinentes.",
            "Construire une proposition minimale.",
            "Demander l'approbation avant application.",
        ]

        verification=[
            "Rejouer le contrôle qui a échoué.",
            "Vérifier le fichier directement modifié.",
            "Vérifier les dépendances directes affectées.",
            "Contrôler les diagnostics nouveaux ou persistants.",
        ]

        diagnosis=f"Erreur {error_kind} sur {change_target}: {error_message}"

        return RepairPlan(
            context=context,
            diagnosis=diagnosis,
            likely_causes=causes,
            repair_steps=steps,
            verification_steps=verification,
            approval_required=True,
        )
