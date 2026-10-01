from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from berkios.intelligence.unified import UnifiedIntelligence

@dataclass
class PreparedRunContext:
    snapshot: dict[str, Any]
    run_memory: list[dict[str, Any]]

    def to_dict(self):
        return {
            "snapshot": self.snapshot,
            "run_memory": self.run_memory,
        }

class AgentRunContext:
    """Connects Unified Intelligence to an agent run.

    The adapter is intentionally tolerant of different RunMemory APIs so
    it can sit above the existing runtime without coupling the intelligence
    layer to one storage implementation.
    """

    def __init__(self, workspace, runtime=None, run_memory=None):
        self.intelligence = UnifiedIntelligence(workspace, runtime)
        self.run_memory = run_memory
        self.entries: list[dict[str, Any]] = []

    def prepare(self, request: str, **kwargs) -> PreparedRunContext:
        snapshot = self.intelligence.build(request, **kwargs).to_dict()
        entry = {
            "type": "intelligence.snapshot",
            "request": request,
            "affected_files": snapshot.get("affected_files", []),
            "affected_symbols": snapshot.get("affected_symbols", []),
        }
        self._remember(entry)
        return PreparedRunContext(snapshot=snapshot, run_memory=list(self.entries))

    def record_transition(self, state: str, detail: dict[str, Any] | None = None):
        entry = {
            "type": "agent.transition",
            "state": state,
            "detail": detail or {},
        }
        self._remember(entry)

    def record_decision(self, decision: dict[str, Any]):
        self._remember({
            "type": "agent.decision",
            "decision": decision,
        })

    def record_verification(self, result: dict[str, Any]):
        self._remember({
            "type": "verification.result",
            "result": result,
        })

    def _remember(self, entry):
        self.entries.append(entry)
        if self.run_memory is None:
            return
        for name in ("add", "remember", "record"):
            method = getattr(self.run_memory, name, None)
            if callable(method):
                try:
                    method(entry)
                    return
                except TypeError:
                    try:
                        method(entry.get("type", "event"), entry)
                        return
                    except Exception:
                        pass
                except Exception:
                    pass
