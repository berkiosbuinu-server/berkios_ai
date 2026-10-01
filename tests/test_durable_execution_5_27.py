def test_execution_controller_can_restore(tmp_path):
    from berkios.persistence import Database, PersistenceRepository
    from berkios.execution.controller import ExecutionController
    from berkios.execution.run import ExecutionRun, RunState

    class Executor:
        def execute_step(self, step, context):
            raise AssertionError("not called")

    class P:
        pass

    p = P()
    p.repository = PersistenceRepository(Database(f"sqlite:///{tmp_path / 'db.sqlite'}"))

    first = ExecutionController(Executor(), persistence=p)
    run = first.create("hello")
    run.state = RunState.PAUSED
    first._persist(run)

    second = ExecutionController(Executor(), persistence=p)
    restored = second.get(run.run_id)
    assert restored is not None
    assert restored.state == RunState.PAUSED
    assert restored.request == "hello"

def test_shared_runtime_factories():
    from berkios.runtime.app import AgentRuntime
    runtime = AgentRuntime(".")
    assert runtime.create_execution_control() is runtime.create_execution_control()
    assert runtime.create_approval_center() is runtime.create_approval_center()
    assert runtime.create_live_bridge() is runtime.create_live_bridge()
    assert runtime.create_persistence() is runtime.create_persistence()
