from berkios.providers.agent_decision import ProviderDecisionAdapter
from berkios.providers.context import ContextAwareProvider
from berkios.runtime.change_cycle import ChangeCycle

class ContextAwareProviderCycle:
    def __init__(self, workspace, *, provider=None, runtime=None,
                 lsp=None, **engines):
        self.context = ContextAwareProvider(workspace, runtime, lsp)
        self.provider = ProviderDecisionAdapter(provider)
        self.cycle = ChangeCycle(workspace, runtime=runtime, **engines)

    def prepare(self, request: str, **kwargs):
        return self.context.build(request, **kwargs)

    def decide(self, request: str, **kwargs):
        context = self.context.build(request, **kwargs)
        decision = self.provider.decide(request, context.to_dict())
        return decision, context

    def propose(self, run_id: str, request: str, **kwargs):
        decision, context = self.decide(request, **kwargs)
        if decision.action in ("propose", "modify", "change"):
            proposal = decision.proposal or {"reason": decision.reason}
            self.cycle.propose(run_id, proposal)
            return decision, context, proposal
        return decision, context, None

    def repair(self, run_id: str, request: str,
               failure: dict, **kwargs):
        context = self.context.build(request, **kwargs).to_dict()
        context["verification_failure"] = failure
        decision = self.provider.decide(request, context)
        repair = decision.repair or decision.proposal
        return decision, context, repair
