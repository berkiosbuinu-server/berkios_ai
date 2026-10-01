from berkios.agent.loop2 import AgentLoop2

class AgentLoop2Controller:
    def __init__(self, runtime, **kwargs):
        self.loop = AgentLoop2(runtime, **kwargs)

    def run(self, run_id, request, **context):
        return self.loop.run(run_id, request, **context).to_dict()

    def apply(self, run_id, proposal):
        return self.loop.apply_after_approval(run_id, proposal)

    def verify(self, run_id, target=None):
        return self.loop.verify_after_apply(run_id, target)

    def continue_verification(self, run_id, request, verification, **context):
        return self.loop.continue_after_verification(
            run_id, request, verification, **context
        )
