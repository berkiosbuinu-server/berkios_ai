from berkios.runtime.agent_loop_runtime import AgentLoopRuntime

class AgentLoopController:
    def __init__(self, agent_runtime, provider=None, lsp=None):
        self.loop = AgentLoopRuntime(agent_runtime, provider, lsp)

    def analyze(self, run_id, request, **kwargs):
        return self.loop.analyze(run_id, request, **kwargs)

    def propose(self, run_id, request, **kwargs):
        return self.loop.propose(run_id, request, **kwargs)

    def repair(self, run_id, request, failure, **kwargs):
        return self.loop.repair(run_id, request, failure, **kwargs)
