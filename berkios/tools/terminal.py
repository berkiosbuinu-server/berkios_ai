import subprocess
from .base import Tool

class TerminalTool(Tool):
    name = "terminal.execute"
    permission = "terminal.execute"
    requires_confirmation = True
    def __init__(self, workspace): self.workspace = workspace
    def execute(self, argv):
        r = subprocess.run(argv, cwd=self.workspace, shell=False,
                           capture_output=True, text=True)
        return {"returncode": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
