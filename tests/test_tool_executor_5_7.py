from berkios.actionplan import ActionPlanner, CapabilityResolver
from berkios.execution import ExecutionPlanner, ExecutionState, ToolExecutor


class D:
    action = "analyze"
    objective = "Analyser"
    rationale = "test"


def test_executor_runs_only_ready_registered_tools():
    plan = ActionPlanner().plan(D(), "Analyse", {"active_file": "app.py"})
    matches = CapabilityResolver().resolve(plan)
    execution = ExecutionPlanner().build(plan, matches)

    executor = ToolExecutor()
    called = []

    executor.register(
        "project.search",
        lambda **kwargs: called.append(kwargs["step"].id) or {"ok": True}
    )

    results = executor.execute_ready(execution)
    assert called
    assert results[0].success is True


def test_executor_does_not_bypass_approval():
    class ChangeDecision:
        action = "analyze_and_propose_change"
        objective = "Modifier"
        rationale = "test"

    plan = ActionPlanner().plan(
        ChangeDecision(), "Modifie", {"active_file": "app.py"}
    )
    matches = CapabilityResolver().resolve(plan)
    execution = ExecutionPlanner().build(plan, matches)
    executor = ToolExecutor()
    executor.register("changes.propose", lambda **_: {"changed": True})

    result = executor.execute_step(execution.steps[2])
    assert result.state == ExecutionState.WAITING_APPROVAL
    assert result.success is False
