from berkios.runtime.agent_runtime import AgentRuntime, RuntimeState

class RuntimeController:
    def __init__(self, workspace, runtime=None, run_memory=None):
        self.agent = AgentRuntime(workspace, runtime, run_memory)

    def start(self, request, **kwargs):
        return self.agent.start(request, **kwargs).to_dict()

    def transition(self, run_id, state, **detail):
        return self.agent.transition(run_id, RuntimeState(state), **detail).to_dict()

    def decision(self, run_id, decision):
        return self.agent.record_decision(run_id, decision).to_dict()

    def verification(self, run_id, result):
        return self.agent.record_verification(run_id, result).to_dict()

    def complete(self, run_id, result=None):
        return self.agent.complete(run_id, result).to_dict()

    def fail(self, run_id, error):
        return self.agent.fail(run_id, error).to_dict()
