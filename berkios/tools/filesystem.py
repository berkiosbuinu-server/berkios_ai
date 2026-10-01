from pathlib import Path
from .base import Tool

class FilesystemTool(Tool):
    name = "filesystem.read"
    permission = "project.read"
    def __init__(self, workspace): self.workspace = Path(workspace)
    def execute(self, path):
        p = (self.workspace / path).resolve()
        if self.workspace not in p.parents and p != self.workspace: raise ValueError("Outside workspace")
        return {"path": path, "content": p.read_text(encoding="utf-8")}
