from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class RepairContext:
    request: str
    failure: dict[str, Any]
    diagnosis: list[Any] = field(default_factory=list)
    historical_errors: list[Any] = field(default_factory=list)
    corrections: list[Any] = field(default_factory=list)
    semantic_context: list[Any] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    affected_symbols: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "request": self.request,
            "failure": self.failure,
            "diagnosis": self.diagnosis,
            "historical_errors": self.historical_errors,
            "corrections": self.corrections,
            "semantic_context": self.semantic_context,
            "affected_files": self.affected_files,
            "affected_symbols": self.affected_symbols,
        }

class ErrorGuidedRepairContext:
    def __init__(self, workspace, runtime=None):
        self.workspace = workspace
        self.runtime = runtime

    def build(self, request: str, failure: dict[str, Any],
              affected_files=None, affected_symbols=None):
        error_manager = getattr(self.runtime, "errors", None) if self.runtime else None
        history = getattr(self.runtime, "error_history", None) if self.runtime else None
        corrections = getattr(self.runtime, "corrections", None) if self.runtime else None
        semantic = getattr(self.runtime, "semantic_memory", None) if self.runtime else None

        diagnosis = self._call(error_manager, ("diagnose", "analyze"), failure)
        historical = self._call(history, ("similar", "search"), failure)
        correction_items = self._call(corrections, ("recall", "search"), failure)
        semantic_items = self._call(semantic, ("context", "search"), request)

        return RepairContext(
            request=request,
            failure=failure,
            diagnosis=self._as_list(diagnosis),
            historical_errors=self._as_list(historical),
            corrections=self._as_list(correction_items),
            semantic_context=self._as_list(semantic_items),
            affected_files=affected_files or [],
            affected_symbols=affected_symbols or [],
        )

    def _call(self, obj, names, value):
        if obj is None:
            return []
        for name in names:
            method = getattr(obj, name, None)
            if callable(method):
                try:
                    return method(value)
                except TypeError:
                    try:
                        return method()
                    except Exception:
                        pass
                except Exception:
                    pass
        return []

    def _as_list(self, value):
        if value is None:
            return []
        return value if isinstance(value, list) else [value]
