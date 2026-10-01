from berkios.agent.repair_loop import ErrorGuidedRepairLoop

class RepairController:
    def __init__(self, runtime, provider=None):
        self.loop = ErrorGuidedRepairLoop(runtime, provider)

    def prepare(self, run_id, request, failure, **kwargs):
        return self.loop.prepare(run_id, request, failure, **kwargs).to_dict()

    def decide(self, run_id, request, failure, **kwargs):
        decision, context = self.loop.decide(
            run_id, request, failure, **kwargs
        )
        return {
            "decision": decision.to_dict(),
            "context": context.to_dict(),
        }
