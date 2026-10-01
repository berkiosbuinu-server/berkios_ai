from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from berkios.runtime.agent_runtime import AgentRuntime, RuntimeState

@dataclass
class CycleResult:
    run_id: str
    status: str
    proposal: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)
    repair: dict[str, Any] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "status": self.status,
            "proposal": self.proposal,
            "verification": self.verification,
            "repair": self.repair,
            "events": self.events,
        }

class ChangeCycle:
    """Concrete proposal/apply/verify/repair orchestration."""

    def __init__(self, workspace, *,
                 runtime=None,
                 run_memory=None,
                 changes=None,
                 verification=None,
                 permissions=None):
        self.agent = AgentRuntime(workspace, runtime, run_memory)
        self.changes = changes
        self.verification = verification
        self.permissions = permissions

    def start(self, request: str, **kwargs):
        return self.agent.start(request, **kwargs)

    def propose(self, run_id: str, proposal: dict[str, Any]):
        self.agent.transition(run_id, RuntimeState.PROPOSING)
        self.agent.record_decision(run_id, {
            "type": "change.proposal",
            "proposal": proposal,
        })
        return proposal

    def apply(self, run_id: str, proposal: dict[str, Any]):
        self.agent.transition(run_id, RuntimeState.APPLYING)
        if self.changes is None:
            return {"ok": False, "error": "change_engine_unavailable"}

        for name in ("apply", "execute"):
            method = getattr(self.changes, name, None)
            if callable(method):
                try:
                    result = method(proposal)
                    if isinstance(result, dict):
                        return result
                    return {"ok": bool(result), "result": result}
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
        return {"ok": False, "error": "change_engine_method_unavailable"}

    def verify(self, run_id: str, target=None):
        self.agent.transition(run_id, RuntimeState.VERIFYING)
        if self.verification is None:
            return {"ok": False, "error": "verification_engine_unavailable"}

        for name in ("verify", "run", "check"):
            method = getattr(self.verification, name, None)
            if callable(method):
                try:
                    result = method(target) if target is not None else method()
                    if isinstance(result, dict):
                        return result
                    return {"ok": bool(result), "result": result}
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
        return {"ok": False, "error": "verification_method_unavailable"}

    def repair(self, run_id: str, failure: dict[str, Any]):
        self.agent.transition(
            run_id,
            RuntimeState.FAILED,
            repair_requested=True,
        )
        repair = {
            "requested": True,
            "reason": failure.get("error", "verification_failed"),
            "verification": failure,
            "next_action": "propose_repair",
        }
        self.agent.record_decision(run_id, {
            "type": "repair.request",
            "repair": repair,
        })
        return repair

    def finish(self, run_id: str, verification: dict[str, Any]):
        self.agent.record_verification(run_id, verification)
        if verification.get("ok"):
            self.agent.complete(run_id, verification)
            return CycleResult(
                run_id=run_id,
                status="completed",
                verification=verification,
            )
        repair = self.repair(run_id, verification)
        return CycleResult(
            run_id=run_id,
            status="repair_required",
            verification=verification,
            repair=repair,
        )
