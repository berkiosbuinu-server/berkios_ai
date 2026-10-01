from berkios.runtime.orchestrator import RuntimeOrchestrator

class OrchestrationController:
    def __init__(self, workspace, **engines):
        self.runtime = RuntimeOrchestrator(workspace, **engines)

    def start(self, request, **kwargs):
        return self.runtime.start(request, **kwargs).to_dict()

    def propose(self, run_id, proposal):
        return self.runtime.propose_change(run_id, proposal).to_dict()

    def permission(self, run_id, action, scope):
        return self.runtime.request_permission(run_id, action, scope).to_dict()

    def approve(self, run_id, action, scope):
        return self.runtime.approve(run_id, action, scope).to_dict()

    def verify(self, run_id, result):
        return self.runtime.verify(run_id, result).to_dict()
