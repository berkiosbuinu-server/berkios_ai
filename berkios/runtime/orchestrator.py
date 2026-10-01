from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from berkios.runtime.agent_runtime import AgentRuntime, RuntimeState

@dataclass
class ExecutionResult:
    run_id: str
    ok: bool
    stage: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "ok": self.ok,
            "stage": self.stage,
            "data": self.data,
        }

class RuntimeOrchestrator:
    """Coordinates the major execution engines around AgentRuntime.

    Engines are optional and injected, keeping the orchestration layer
    independent from concrete implementations.
    """

    def __init__(self, workspace, *,
                 runtime=None,
                 run_memory=None,
                 permissions=None,
                 changes=None,
                 verification=None,
                 providers=None):
        self.agent = AgentRuntime(workspace, runtime, run_memory)
        self.permissions = permissions
        self.changes = changes
        self.verification = verification
        self.providers = providers

    def start(self, request: str, **kwargs):
        run = self.agent.start(request, **kwargs)
        return run

    def request_permission(self, run_id: str, action: str, scope: str):
        run = self.agent.transition(
            run_id,
            RuntimeState.WAITING_APPROVAL,
            action=action,
            scope=scope,
        )
        return ExecutionResult(
            run_id, True, "waiting_approval",
            {"action": action, "scope": scope},
        )

    def approve(self, run_id: str, action: str, scope: str):
        if self.permissions is not None:
            for name in ("grant", "approve", "allow"):
                method = getattr(self.permissions, name, None)
                if callable(method):
                    try:
                        method(action, scope)
                        break
                    except TypeError:
                        try:
                            method(scope)
                            break
                        except Exception:
                            pass
                    except Exception:
                        pass
        self.agent.transition(run_id, RuntimeState.APPLYING, action=action)
        return ExecutionResult(run_id, True, "approved", {"action": action})

    def propose_change(self, run_id: str, proposal: dict[str, Any]):
        self.agent.transition(run_id, RuntimeState.PROPOSING)
        self.agent.record_decision(run_id, {
            "type": "change.proposal",
            "proposal": proposal,
        })
        return ExecutionResult(
            run_id, True, "proposed", {"proposal": proposal}
        )

    def verify(self, run_id: str, result: dict[str, Any]):
        self.agent.record_verification(run_id, result)
        ok = bool(result.get("ok"))
        if ok:
            self.agent.complete(run_id, result)
            return ExecutionResult(run_id, True, "completed", result)
        self.agent.fail(
            run_id,
            result.get("error", "verification failed"),
        )
        return ExecutionResult(run_id, False, "failed", result)

    def provider(self, capability: str):
        if self.providers is None:
            return None
        for name in ("select", "choose", "get"):
            method = getattr(self.providers, name, None)
            if callable(method):
                try:
                    return method(capability)
                except Exception:
                    pass
        return None
