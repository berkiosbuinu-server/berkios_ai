from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from berkios.graph.intelligence import ProjectGraphIntelligence

@dataclass
class IntelligenceSnapshot:
    request: str
    workspace: str
    active_file: str | None = None
    selection: str | None = None
    diagnostics: list[Any] = field(default_factory=list)
    recent_files: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)
    graph_context: dict[str, Any] = field(default_factory=dict)
    memories: list[Any] = field(default_factory=list)
    corrections: list[Any] = field(default_factory=list)
    errors: list[Any] = field(default_factory=list)
    git: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "request": self.request,
            "workspace": self.workspace,
            "active_file": self.active_file,
            "selection": self.selection,
            "diagnostics": self.diagnostics,
            "recent_files": self.recent_files,
            "affected_files": self.affected_files,
            "affected_symbols": self.affected_symbols,
            "graph_context": self.graph_context,
            "memories": self.memories,
            "corrections": self.corrections,
            "errors": self.errors,
            "git": self.git,
            "verification": self.verification,
        }

class UnifiedIntelligence:
    """Orchestrates the project intelligence sources into one snapshot.

    Optional runtime components are detected defensively so the layer can
    be introduced without forcing every integration to exist at once.
    """

    def __init__(self, workspace, runtime=None):
        self.workspace = workspace
        self.runtime = runtime
        self.graph = ProjectGraphIntelligence(workspace)

    def build(self, request: str, active_file: str | None = None,
              selection: str | None = None, target_nodes: list[str] | None = None):
        target_nodes = target_nodes or []
        affected_files = set()
        affected_symbols = set()
        graph_context = {}

        for node_id in target_nodes:
            report = self.graph.impact(node_id, depth=2)
            affected_files.update(report.affected_files)
            affected_symbols.update(report.affected_symbols)
            graph_context[node_id] = report.to_dict()

        memories = self._optional_memory("semantic_memory", request)
        corrections = self._optional_memory("corrections", request)
        errors = self._optional_memory("error_history", request)
        git = self._optional_git()
        diagnostics = self._optional_context("diagnostics")
        recent_files = self._optional_context("recent_files")

        return IntelligenceSnapshot(
            request=request,
            workspace=str(self.workspace),
            active_file=active_file,
            selection=selection,
            diagnostics=diagnostics,
            recent_files=recent_files,
            affected_files=sorted(affected_files),
            affected_symbols=sorted(affected_symbols),
            graph_context=graph_context,
            memories=memories,
            corrections=corrections,
            errors=errors,
            git=git,
        )

    def _optional_context(self, name):
        ctx = getattr(self.runtime, "live_context", None) if self.runtime else None
        value = getattr(ctx, name, None) if ctx else None
        if callable(value):
            try:
                value = value()
            except Exception:
                return []
        return value or []

    def _optional_memory(self, component, query):
        obj = getattr(self.runtime, component, None) if self.runtime else None
        if obj is None:
            return []
        for method_name in ("search", "recall", "context"):
            method = getattr(obj, method_name, None)
            if callable(method):
                try:
                    value = method(query)
                    return value if isinstance(value, list) else [value]
                except TypeError:
                    try:
                        value = method()
                        return value if isinstance(value, list) else [value]
                    except Exception:
                        pass
                except Exception:
                    pass
        return []

    def _optional_git(self):
        git = getattr(self.runtime, "git", None) if self.runtime else None
        if git is None:
            return {}
        for name in ("status", "snapshot"):
            method = getattr(git, name, None)
            if callable(method):
                try:
                    value = method()
                    return value if isinstance(value, dict) else {"value": value}
                except Exception:
                    pass
        return {}
