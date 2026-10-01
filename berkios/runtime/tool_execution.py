from __future__ import annotations
from berkios.execution import ToolExecutor


class RuntimeToolExecutor:
    def __init__(self, runtime):
        self.runtime = runtime
        self.executor = ToolExecutor()

    def register(self, capability, handler):
        self.executor.register(capability, handler)

    def execute(self, plan, context=None):
        return self.executor.execute_ready(plan, context or {})
