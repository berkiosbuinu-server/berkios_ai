from berkios.runtime.context_provider_cycle import ContextAwareProviderCycle

class ContextProviderController:
    def __init__(self, workspace, **kwargs):
        self.runtime = ContextAwareProviderCycle(workspace, **kwargs)

    def prepare(self, request, **kwargs):
        return self.runtime.prepare(request, **kwargs).to_dict()

    def decide(self, request, **kwargs):
        decision, context = self.runtime.decide(request, **kwargs)
        return {
            "decision": decision.to_dict(),
            "context": context.to_dict(),
        }

    def propose(self, run_id, request, **kwargs):
        decision, context, proposal = self.runtime.propose(
            run_id, request, **kwargs
        )
        return {
            "decision": decision.to_dict(),
            "context": context.to_dict(),
            "proposal": proposal,
        }
