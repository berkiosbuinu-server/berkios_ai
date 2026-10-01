from __future__ import annotations
from typing import Any
from berkios.providers.context import ContextAwareProvider
from berkios.providers.agent_decision import AgentDecision
from berkios.runtime.agent_runtime import RuntimeState

class ContextAwareAgentLoop:
    """AgentLoop facade using the same enriched provider context for all decisions."""

    def __init__(self, runtime, provider=None, lsp=None):
        self.runtime = runtime
        self.provider_context = ContextAwareProvider(
            runtime.workspace,
            getattr(runtime, "runtime", None),
            lsp,
        )
        from berkios.providers.agent_decision import ProviderDecisionAdapter
        self.provider = ProviderDecisionAdapter(provider)

    def prepare_context(self, request: str, **kwargs):
        return self.provider_context.build(request, **kwargs)

    def analyze(self, run_id: str, request: str, **kwargs):
        context = self.prepare_context(request, **kwargs)
        self.runtime.transition(
            run_id,
            RuntimeState.ANALYZING,
            context_ready=True,
        )
        decision = self.provider.decide(request, context.to_dict())
        self.runtime.record_decision(
            run_id,
            {"phase": "analysis", "decision": decision.to_dict()},
        )
        return decision, context

    def propose(self, run_id: str, request: str, **kwargs):
        context = self.prepare_context(request, **kwargs)
        self.runtime.transition(run_id, RuntimeState.PROPOSING)
        decision = self.provider.decide(request, context.to_dict())
        self.runtime.record_decision(
            run_id,
            {"phase": "proposal", "decision": decision.to_dict()},
        )
        return decision, context

    def repair(self, run_id: str, request: str,
               failure: dict[str, Any], **kwargs):
        context = self.prepare_context(request, **kwargs).to_dict()
        context["verification_failure"] = failure
        decision = self.provider.decide(request, context)
        self.runtime.record_decision(
            run_id,
            {"phase": "repair", "decision": decision.to_dict()},
        )
        return decision, context
