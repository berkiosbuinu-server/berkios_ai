from __future__ import annotations
from berkios.execution import ExecutionPlanner


class RuntimeExecutionPlanner:
    def __init__(self, runtime):
        self.runtime = runtime
        self.planner = ExecutionPlanner()

    def build(self, action_plan, capability_matches=None):
        return self.planner.build(action_plan, capability_matches)
