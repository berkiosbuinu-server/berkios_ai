from berkios.execution import (
    ExecutionController, ExecutionPlan, ExecutionStep, ExecutionState, ToolExecutor
)


def test_execution_run_records_events_and_results():
    executor = ToolExecutor()
    executor.register(
        "demo",
        lambda **_: {"ok": True}
    )
    controller = ExecutionController(executor)
    run = controller.create("demo")
    plan = ExecutionPlan(
        request="demo",
        steps=[
            ExecutionStep(
                id="x1",
                action_id="a1",
                capability="demo",
                state=ExecutionState.READY,
            )
        ],
    )
    result = controller.execute(run.run_id, plan)
    assert result.state.value == "completed"
    assert result.results[0]["success"] is True
    assert any(e["event"] == "execution.completed" for e in result.events)


def test_cancelled_run_does_not_execute():
    called = []
    executor = ToolExecutor()
    executor.register("demo", lambda **_: called.append(1))
    controller = ExecutionController(executor)
    run = controller.create("demo")
    controller.cancel(run.run_id)

    plan = ExecutionPlan(
        request="demo",
        steps=[ExecutionStep(
            id="x1", action_id="a1", capability="demo",
            state=ExecutionState.READY
        )]
    )
    result = controller.execute(run.run_id, plan)
    assert result.state.value == "cancelled"
    assert not called
