from berkios.execution import ExecutionController, ToolExecutor
from berkios.ibook.live import IBookLiveBridge


def test_live_bridge_snapshot_and_events():
    controller = ExecutionController(ToolExecutor())
    run = controller.create("test")
    bridge = IBookLiveBridge(controller)

    snap = bridge.snapshot(run.run_id)
    assert snap.state == "created"
    assert snap.event_count == 1

    events = bridge.events(run.run_id)
    assert events[0]["event"] == "execution.created"


def test_live_bridge_cancel():
    controller = ExecutionController(ToolExecutor())
    run = controller.create("test")
    bridge = IBookLiveBridge(controller)
    result = bridge.cancel(run.run_id)
    assert result.state.value == "cancelled"
