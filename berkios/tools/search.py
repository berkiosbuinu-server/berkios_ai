from pathlib import Path
from .base import Tool

class SearchTool(Tool):
    name = "filesystem.search"
    permission = "project.read"
    def __init__(self, workspace): self.workspace = Path(workspace)
    def execute(self, query):
        hits = []
        for p in self.workspace.rglob("*"):
            if p.is_file() and ".berkios" not in p.parts:
                try:
                    if query.lower() in p.read_text(encoding="utf-8").lower():
                        hits.append(str(p.relative_to(self.workspace)))
                except (UnicodeDecodeError, OSError):
                    pass
        return {"query": query, "hits": hits}
