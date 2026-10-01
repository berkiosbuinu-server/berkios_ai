from __future__ import annotations
from pathlib import Path
from .models import LSPResult

class LSPService:
    """Transport-neutral LSP facade for iBook/Berkios integrations.

    A real language-server transport can be plugged in without changing the
    public API used by the agent.
    """
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)

    def diagnostics(self, path: str) -> LSPResult:
        return LSPResult(operation="diagnostics", items=[], raw={"path": path})

    def definition(self, path: str, line: int, character: int) -> LSPResult:
        return LSPResult(operation="definition", items=[], raw={
            "path": path, "line": line, "character": character
        })

    def references(self, path: str, line: int, character: int) -> LSPResult:
        return LSPResult(operation="references", items=[], raw={
            "path": path, "line": line, "character": character
        })
