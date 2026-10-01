from pathlib import Path
from berkios.runtime.agent_runtime import AgentRuntime, RuntimeState

def test_canonical_runtime(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    runtime = AgentRuntime(tmp_path)
    run = runtime.start("modify A", active_file="a.py", target_nodes=["file:a.py"])
    assert run.state == RuntimeState.ANALYZING
    runtime.transition(run.run_id, RuntimeState.PLANNING)
    runtime.record_decision(run.run_id, {"action": "propose"})
    runtime.complete(run.run_id, {"ok": True})
    assert runtime.get(run.run_id).state == RuntimeState.COMPLETED
    assert len(runtime.get(run.run_id).events) >= 3
