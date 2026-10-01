from __future__ import annotations
from berkios.execution import ExecutionResumer


class RuntimeExecutionResumer:
    def __init__(self, runtime):
        self.runtime = runtime
        self.resumer = ExecutionResumer()

    def checkpoint(self, run, plan):
        return self.resumer.checkpoint(run, plan)

    def ready_steps(self, run, plan):
        return self.resumer.ready_steps(run, plan)
