from berkios.execution import (
    ExecutionController, ExecutionPlan, ExecutionStep,
    ExecutionState, ToolExecutor, ExecutionResumer
)


def test_resume_skips_completed_steps():
    controller = ExecutionController(ToolExecutor())
    run = controller.create("resume")
    run.results.append({
        "step_id": "x1",
        "success": True,
        "state": "completed",
    })
    plan = ExecutionPlan(
        request="resume",
        steps=[
            ExecutionStep("x1","a1","one",ExecutionState.READY),
            ExecutionStep("x2","a2","two",ExecutionState.READY,["x1"]),
        ],
    )
    point = ExecutionResumer().checkpoint(run, plan)
    assert point.completed_steps == ["x1"]
    assert point.next_step_id == "x2"
    assert [x.id for x in ExecutionResumer().ready_steps(run, plan)] == ["x2"]
