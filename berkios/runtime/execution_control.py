from __future__ import annotations
from berkios.execution import ExecutionController

class RuntimeExecutionControl:
    def __init__(self, runtime):
        self.runtime = runtime
        self.controller = ExecutionController(
            runtime.create_tool_executor().executor,
            persistence=runtime.create_persistence(),
        )

    def create(self, request):
        return self.controller.create(request)

    def execute(self, run_id, plan, context=None):
        return self.controller.execute(run_id, plan, context or {})

    def get(self, run_id):
        return self.controller.get(run_id)

    def pause(self, run_id):
        return self.controller.pause(run_id)

    def cancel(self, run_id):
        return self.controller.cancel(run_id)
