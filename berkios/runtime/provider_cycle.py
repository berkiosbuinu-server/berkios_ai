from __future__ import annotations
from typing import Any

from berkios.providers.agent_decision import ProviderDecisionAdapter
from berkios.runtime.change_cycle import ChangeCycle

class ProviderDrivenCycle:
    """Connects a provider decision to the change/repair cycle."""

    def __init__(self, workspace, *, provider=None, **engines):
        self.provider = ProviderDecisionAdapter(provider)
        self.cycle = ChangeCycle(workspace, **engines)

    def decide(self, request: str, context: dict[str, Any]):
        return self.provider.decide(request, context)

    def propose_from_provider(self, run_id: str, request: str,
                              context: dict[str, Any]):
        decision = self.decide(request, context)
        if decision.action in ("propose", "modify", "change"):
            proposal = decision.proposal or {
                "reason": decision.reason,
            }
            return decision, self.cycle.propose(run_id, proposal)
        return decision, None

    def repair_from_provider(self, run_id: str, request: str,
                             context: dict[str, Any],
                             failure: dict[str, Any]):
        merged = dict(context)
        merged["verification_failure"] = failure
        decision = self.decide(request, merged)
        if decision.action in ("repair", "fix", "modify"):
            repair = decision.repair or decision.proposal or {
                "reason": decision.reason,
                "failure": failure,
            }
            return decision, repair
        return decision, None
