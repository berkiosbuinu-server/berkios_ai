from dataclasses import dataclass

@dataclass
class VerificationResult:
    ok: bool
    checks: list
    repair_hint: str = ""

class VerificationLoop:
    def __init__(self, engine, max_repairs=2):
        self.engine = engine
        self.max_repairs = max_repairs

    def verify_files(self, paths):
        result = self.engine.files(paths)
        return VerificationResult(
            ok=result["ok"],
            checks=[result],
            repair_hint="" if result["ok"] else "Vérifier les fichiers attendus."
        )
