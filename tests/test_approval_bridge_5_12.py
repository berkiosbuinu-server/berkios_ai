from berkios.approval import ApprovalManager, ApprovalExecutionBridge
from berkios.execution import ExecutionController, ToolExecutor


def test_approval_is_bound_to_step_and_run():
    approvals = ApprovalManager()
    execution = ExecutionController(ToolExecutor())
    run = execution.create("modify")

    bridge = ApprovalExecutionBridge(approvals, execution)
    request = approvals.create(
        run_id=run.run_id,
        action_id="a3",
        capability="changes.propose",
        title="Modifier",
    )
    bridge.bind(request, "x_a3")

    approved = bridge.decide(request.approval_id, True)
    assert approved.decision.value == "approved"
    assert run.events[-1]["event"] == "approval.approved"
    assert run.events[-1]["data"]["step_id"] == "x_a3"


def test_rejected_approval_is_not_approved():
    approvals = ApprovalManager()
    execution = ExecutionController(ToolExecutor())
    bridge = ApprovalExecutionBridge(approvals, execution)
    request = approvals.create(title="Danger")
    bridge.bind(request, "x1")
    bridge.decide(request.approval_id, False)
    assert bridge.is_approved(request.approval_id) is False
