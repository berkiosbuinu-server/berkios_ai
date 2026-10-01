from pathlib import Path
import ast
import subprocess
import sys
from .models import VerificationFinding, VerificationReport

class VerificationIntelligence:
    """Relie les résultats de vérification au changement et à son impact."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()

    def inspect_files(self, change_target, targets):
        findings=[]
        verified=[]
        skipped=[]

        for target in targets:
            p=(self.workspace/target).resolve()
            if not p.is_file():
                skipped.append(target)
                findings.append(VerificationFinding(
                    target,"skipped","warning",
                    "Fichier introuvable pour la vérification.",
                    change_target))
                continue

            verified.append(target)

            if p.suffix==".py":
                try:
                    ast.parse(p.read_text(encoding="utf-8",errors="replace"),filename=str(p))
                    findings.append(VerificationFinding(
                        target,"passed","info",
                        "Syntaxe Python valide.",
                        change_target))
                except SyntaxError as e:
                    findings.append(VerificationFinding(
                        target,"failed","error",
                        f"Erreur de syntaxe ligne {e.lineno}: {e.msg}",
                        change_target))
            else:
                findings.append(VerificationFinding(
                    target,"passed","info",
                    "Fichier accessible et sélectionné pour vérification.",
                    change_target))

        failed=[f for f in findings if f.status=="failed"]
        passed=not failed
        if failed:
            summary=f"{len(failed)} vérification(s) ont échoué."
            next_action="Analyser les erreurs puis proposer une correction ciblée."
        elif skipped:
            summary=f"Vérification terminée avec {len(skipped)} élément(s) ignoré(s)."
            next_action="Vérifier les cibles ignorées si elles sont nécessaires."
        else:
            summary=f"{len(verified)} cible(s) vérifiée(s) avec succès."
            next_action="Continuer le cycle ou enregistrer la correction comme validée."

        return VerificationReport(
            change_target=change_target,
            passed=passed,
            findings=findings,
            verified_targets=verified,
            skipped_targets=skipped,
            summary=summary,
            next_action=next_action,
        )

    def run_python_check(self, target):
        p=(self.workspace/target).resolve()
        if p.suffix!=".py":
            return {"status":"skipped","message":"Pas un fichier Python."}
        proc=subprocess.run(
            [sys.executable,"-m","py_compile",str(p)],
            cwd=str(self.workspace),
            capture_output=True,
            text=True,
            shell=False,
        )
        return {
            "status":"passed" if proc.returncode==0 else "failed",
            "stdout":proc.stdout,
            "stderr":proc.stderr,
            "returncode":proc.returncode,
        }
