from pathlib import Path
from berkios.runtime.agent_runtime import AgentRuntime
from berkios.agent.context_loop import ContextAwareAgentLoop

class FakeProvider:
    def decide(self, request, context):
        return {
            "action": "propose",
            "proposal": {"files": context["ibook"].get("recent_files", [])},
        }

def test_context_loop(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    runtime = AgentRuntime(tmp_path)
    run = runtime.start("modify A", active_file="a.py")
    loop = ContextAwareAgentLoop(runtime, provider=FakeProvider())
    decision, context = loop.propose(
        run.run_id,
        "modify A",
        active_file="a.py",
        target_nodes=["file:a.py"],
    )
    assert decision.action == "propose"
    assert context.ibook["active_file"] == "a.py"
    assert any(e["kind"] == "agent.decision" for e in run.events)
