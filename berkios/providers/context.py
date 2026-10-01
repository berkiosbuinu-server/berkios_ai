from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from berkios.intelligence.unified import UnifiedIntelligence

@dataclass
class ProviderContext:
    request: str
    intelligence: dict[str, Any]
    lsp: dict[str, Any]
    errors: list[Any]
    corrections: list[Any]
    memory: list[Any]
    ibook: dict[str, Any]

    def to_dict(self):
        return {
            "request": self.request,
            "intelligence": self.intelligence,
            "lsp": self.lsp,
            "errors": self.errors,
            "corrections": self.corrections,
            "memory": self.memory,
            "ibook": self.ibook,
        }

class ContextAwareProvider:
    """Builds the provider-facing context from available project sources."""

    def __init__(self, workspace, runtime=None, lsp=None):
        self.workspace = workspace
        self.runtime = runtime
        self.lsp = lsp
        self.intelligence = UnifiedIntelligence(workspace, runtime)

    def build(self, request: str, *,
              active_file=None,
              selection=None,
              target_nodes=None) -> ProviderContext:
        snapshot = self.intelligence.build(
            request,
            active_file=active_file,
            selection=selection,
            target_nodes=target_nodes or [],
        ).to_dict()

        lsp_data = self._lsp_context(active_file)
        errors = snapshot.get("errors", [])
        corrections = snapshot.get("corrections", [])
        memory = snapshot.get("memories", [])

        ibook = {
            "active_file": active_file,
            "selection": selection,
            "recent_files": snapshot.get("recent_files", []),
            "diagnostics": snapshot.get("diagnostics", []),
        }

        return ProviderContext(
            request=request,
            intelligence=snapshot,
            lsp=lsp_data,
            errors=errors,
            corrections=corrections,
            memory=memory,
            ibook=ibook,
        )

    def _lsp_context(self, active_file):
        if not active_file or self.lsp is None:
            return {}
        result = {}
        for name in ("diagnostics",):
            method = getattr(self.lsp, name, None)
            if callable(method):
                try:
                    value = method(active_file)
                    result[name] = value.to_dict() if hasattr(value, "to_dict") else value
                except Exception as exc:
                    result[name] = {"error": str(exc)}
        return result
