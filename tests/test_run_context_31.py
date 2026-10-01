from pathlib import Path
from berkios.agent.run_context import AgentRunContext

def test_run_context(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    context = AgentRunContext(tmp_path)
    prepared = context.prepare(
        "modify A",
        active_file="a.py",
        target_nodes=["file:a.py"],
    )
    assert prepared.snapshot["request"] == "modify A"
    assert prepared.run_memory
    context.record_transition("proposing")
    assert len(context.entries) >= 2
