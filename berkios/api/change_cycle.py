from berkios.runtime.change_cycle import ChangeCycle

class ChangeCycleController:
    def __init__(self, workspace, **engines):
        self.cycle = ChangeCycle(workspace, **engines)

    def start(self, request, **kwargs):
        return self.cycle.start(request, **kwargs).to_dict()

    def propose(self, run_id, proposal):
        return self.cycle.propose(run_id, proposal)

    def apply(self, run_id, proposal):
        return self.cycle.apply(run_id, proposal)

    def verify(self, run_id, target=None):
        return self.cycle.verify(run_id, target)

    def repair(self, run_id, failure):
        return self.cycle.repair(run_id, failure)

    def finish(self, run_id, verification):
        return self.cycle.finish(run_id, verification).to_dict()
