from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from berkios.runtime.agent_runtime import RuntimeState
from berkios.agent.context_loop import ContextAwareAgentLoop

@dataclass
class Loop2Result:
    run_id: str
    status: str
    iterations: int
    decisions: list[dict[str, Any]] = field(default_factory=list)
    verifications: list[dict[str, Any]] = field(default_factory=list)
    repairs: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "status": self.status,
            "iterations": self.iterations,
            "decisions": self.decisions,
            "verifications": self.verifications,
            "repairs": self.repairs,
        }

class AgentLoop2:
    """Bounded proposal/approval/apply/verify/repair loop.

    The runtime remains responsible for permissions. This loop only
    coordinates the stages and stops when approval or verification
    requires external input.
    """

    def __init__(self, runtime, provider=None, lsp=None,
                 changes=None, verification=None, max_iterations=3):
        self.runtime = runtime
        self.loop = ContextAwareAgentLoop(runtime, provider=provider, lsp=lsp)
        self.changes = changes
        self.verification = verification
        self.max_iterations = max(1, int(max_iterations))

    def run(self, run_id: str, request: str, **context):
        decisions = []
        verifications = []
        repairs = []

        for iteration in range(1, self.max_iterations + 1):
            decision, provider_context = self.loop.propose(
                run_id, request, **context
            )
            decisions.append({
                "iteration": iteration,
                "decision": decision.to_dict(),
            })

            if decision.action not in ("propose", "modify", "change"):
                self.runtime.transition(
                    run_id,
                    RuntimeState.WAITING_APPROVAL,
                    reason="provider_did_not_propose_change",
                )
                return Loop2Result(
                    run_id, "waiting", iteration,
                    decisions, verifications, repairs
                )

            proposal = decision.proposal
            self.runtime.transition(
                run_id,
                RuntimeState.WAITING_APPROVAL,
                proposal=proposal,
                iteration=iteration,
            )

            # No automatic approval: caller must explicitly continue.
            return Loop2Result(
                run_id, "approval_required", iteration,
                decisions, verifications, repairs
            )

        return Loop2Result(
            run_id, "iteration_limit", self.max_iterations,
            decisions, verifications, repairs
        )

    def apply_after_approval(self, run_id: str, proposal: dict[str, Any]):
        self.runtime.transition(run_id, RuntimeState.APPLYING)
        if self.changes is None:
            return {"ok": False, "error": "change_engine_unavailable"}
        for name in ("apply", "execute"):
            method = getattr(self.changes, name, None)
            if callable(method):
                try:
                    value = method(proposal)
                    return value if isinstance(value, dict) else {
                        "ok": bool(value), "result": value
                    }
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
        return {"ok": False, "error": "change_engine_method_unavailable"}

    def verify_after_apply(self, run_id: str, target=None):
        self.runtime.transition(run_id, RuntimeState.VERIFYING)
        if self.verification is None:
            return {"ok": False, "error": "verification_engine_unavailable"}
        for name in ("verify", "run", "check"):
            method = getattr(self.verification, name, None)
            if callable(method):
                try:
                    value = method(target) if target is not None else method()
                    return value if isinstance(value, dict) else {
                        "ok": bool(value), "result": value
                    }
                except Exception as exc:
                    return {"ok": False, "error": str(exc)}
        return {"ok": False, "error": "verification_method_unavailable"}

    def continue_after_verification(self, run_id: str, request: str,
                                    verification: dict[str, Any],
                                    **context):
        if verification.get("ok"):
            self.runtime.record_verification(run_id, verification)
            self.runtime.complete(run_id, verification)
            return {
                "status": "completed",
                "verification": verification,
            }

        self.runtime.record_verification(run_id, verification)
        self.runtime.transition(
            run_id,
            RuntimeState.REPAIRING,
            failure=verification,
        )

        repair_context = dict(context)
        repair_context["verification_failure"] = verification
        decision, provider_context = self.loop.repair(
            run_id, request, verification, **repair_context
        )
        repair = decision.repair or decision.proposal

        self.runtime.record_decision(run_id, {
            "phase": "repair",
            "decision": decision.to_dict(),
        })

        return {
            "status": "repair_proposed",
            "verification": verification,
            "repair": repair,
            "context": provider_context,
        }
