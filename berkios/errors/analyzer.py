from dataclasses import dataclass

@dataclass
class Diagnosis:
    error_id: str
    summary: str
    causes: list[str]
    evidence: list[str]
    affected_files: list[str]
    suggested_actions: list[str]

    def to_dict(self):
        return self.__dict__.copy()

class ErrorAnalyzer:
    def analyze(self, error):
        causes = []
        actions = []
        kind = error.kind.value

        if kind == "syntax":
            causes.append("Le parseur Python a rejeté la syntaxe.")
            actions.append("Inspecter la ligne signalée et le contexte immédiat.")
        elif kind == "import":
            causes.append("Un module ou symbole importé n'est pas disponible.")
            actions.append("Vérifier le nom, l'environnement Python et les dépendances.")
        elif kind == "type":
            causes.append("Les types ou valeurs utilisés ne correspondent pas à l'opération.")
            actions.append("Comparer les types attendus et réels à l'emplacement signalé.")
        elif kind == "test":
            causes.append("Une assertion ou un test a échoué.")
            actions.append("Reproduire le test isolément puis inspecter la première divergence.")
        elif kind == "runtime":
            causes.append("Une exception a interrompu l'exécution.")
            actions.append("Examiner la dernière frame pertinente et les valeurs du contexte.")
        else:
            causes.append("La cause exacte n'est pas encore déterminée.")
            actions.append("Collecter davantage de sortie et de contexte.")

        return Diagnosis(
            error_id=error.id,
            summary=error.message,
            causes=causes,
            evidence=[x for x in [error.file, str(error.line) if error.line else None, error.stderr.strip()] if x],
            affected_files=[error.file] if error.file else [],
            suggested_actions=actions,
        )
