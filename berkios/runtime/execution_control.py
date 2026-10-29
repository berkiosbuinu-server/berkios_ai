
from __future__ import annotations

from berkios.execution import ExecutionController


class RuntimeExecutionControl:
    """Facade runtime autour du contrôleur d'exécution canonique."""

    def __init__(self, runtime):
        self.runtime = runtime

        self.executor = runtime.create_tool_executor()

        self.controller = ExecutionController(
            self.executor,
            persistence=runtime.create_persistence(),
            runtime=runtime,
        )

    def create(self, request):
        return self.controller.create(request)

    def execute(self, run_id, plan, context=None):
        return self.controller.execute(
            run_id,
            plan,
            context or {},
        )

    def resume(self, run_id, plan, context=None):
        return self.controller.resume(
            run_id,
            plan,
            context or {},
        )

    def get(self, run_id):
        return self.controller.get(run_id)

    def pause(self, run_id):
        return self.controller.pause(run_id)

    def cancel(self, run_id):
        return self.controller.cancel(run_id)
