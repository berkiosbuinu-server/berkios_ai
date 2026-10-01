from pathlib import Path
import subprocess
from ..errors.manager import ErrorManager

class VerificationEngine:
    def __init__(self, workspace, errors=None):
        self.workspace = Path(workspace).resolve()
        self.errors = errors or ErrorManager()

    def files(self, paths):
        errors = []
        for value in paths:
            p = (self.workspace / value).resolve()
            if not p.exists():
                errors.append(f"Missing file: {value}")
        return {"ok": not errors, "errors": errors}

    def command(self, argv, timeout=60, source="verification"):
        result = subprocess.run(argv, cwd=self.workspace, shell=False,
                                capture_output=True, text=True, timeout=timeout)
        parsed = self.errors.ingest_command(
            argv, result.returncode, result.stdout, result.stderr, source
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "errors": [e.to_dict() for e in parsed],
        }
