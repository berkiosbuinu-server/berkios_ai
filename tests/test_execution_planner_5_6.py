from berkios.actionplan import ActionPlanner, CapabilityResolver
from berkios.execution import ExecutionState, ExecutionPlanner


class D:
    action = "analyze_and_propose_change"
    objective = "Corriger"
    rationale = "test"


def test_execution_plan_blocks_after_approval_step():
    plan = ActionPlanner().plan(D(), "Corrige", {"active_file": "app.py"})
    matches = CapabilityResolver().resolve(plan)
    execution = ExecutionPlanner().build(plan, matches)

    assert execution.steps[0].state == ExecutionState.READY
    assert execution.steps[2].state == ExecutionState.WAITING_APPROVAL
    assert execution.steps[3].state == ExecutionState.BLOCKED
    assert execution.blocked_reasons
