from berkios.runtime.provider_cycle import ProviderDrivenCycle

class ProviderCycleController:
    def __init__(self, workspace, **kwargs):
        self.cycle = ProviderDrivenCycle(workspace, **kwargs)

    def decide(self, request, context):
        return self.cycle.decide(request, context).to_dict()

    def propose(self, run_id, request, context):
        decision, proposal = self.cycle.propose_from_provider(
            run_id, request, context
        )
        return {
            "decision": decision.to_dict(),
            "proposal": proposal,
        }

    def repair(self, run_id, request, context, failure):
        decision, repair = self.cycle.repair_from_provider(
            run_id, request, context, failure
        )
        return {
            "decision": decision.to_dict(),
            "repair": repair,
        }
