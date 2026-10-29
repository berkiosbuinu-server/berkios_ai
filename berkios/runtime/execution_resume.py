from __future__ import annotations

from berkios.execution import ExecutionResumer


class RuntimeExecutionResumer:
    def __init__(self, runtime):
        self.runtime = runtime
        self.resumer = ExecutionResumer()

    def checkpoint(self, run, plan):
        return self.resumer.checkpoint(
            run,
            plan,
        )

    def ready_steps(self, run, plan):
        return self.resumer.ready_steps(
            run,
            plan,
        )

    def prepare_resume(self, run, plan):
        return self.resumer.prepare_resume(
            run,
            plan,
        )

    def resume(self, run, plan, context=None):
        self.prepare_resume(
            run,
            plan,
        )

        return self.runtime.create_execution_control().resume(
            run.run_id,
            plan,
            context or run.context or {},
        )
