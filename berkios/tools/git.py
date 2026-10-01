import subprocess
from .base import Tool

class GitTool(Tool):
    name = "git.status"
    permission = "git.read"
    def __init__(self, workspace): self.workspace = workspace
    def execute(self):
        r = subprocess.run(["git", "status", "--short"], cwd=self.workspace,
                           shell=False, capture_output=True, text=True)
        return {"returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
