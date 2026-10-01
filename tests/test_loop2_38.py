from pathlib import Path
from berkios.runtime.agent_runtime import AgentRuntime
from berkios.agent.loop2 import AgentLoop2

class FakeProvider:
    def decide(self, request, context):
        return {
            "action": "propose",
            "proposal": {"files": ["a.py"]},
        }

def test_loop2_stops_for_approval(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    runtime = AgentRuntime(tmp_path)
    run = runtime.start("modify A", active_file="a.py")
    loop = AgentLoop2(runtime, provider=FakeProvider())
    result = loop.run(
        run.run_id,
        "modify A",
        active_file="a.py",
        target_nodes=["file:a.py"],
    )
    assert result.status == "approval_required"
    assert result.iterations == 1
    assert runtime.get(run.run_id).state.value == "waiting_approval"
