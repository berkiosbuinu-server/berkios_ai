from __future__ import annotations
from berkios.actionplan import ActionPlanner


class RuntimeActionPlanner:
    def __init__(self, runtime):
        self.runtime = runtime
        self.planner = ActionPlanner()

    def plan_from_decision(self, decision, request: str, context=None):
        return self.planner.plan(decision, request, context or {})
