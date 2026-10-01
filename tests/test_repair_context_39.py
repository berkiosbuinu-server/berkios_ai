from pathlib import Path
from berkios.runtime.agent_runtime import AgentRuntime
from berkios.intelligence.repair_context import ErrorGuidedRepairContext

def test_error_guided_context(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    runtime = AgentRuntime(tmp_path)
    context = ErrorGuidedRepairContext(tmp_path, runtime)
    result = context.build(
        "repair A",
        {"kind": "test", "message": "failure"},
        affected_files=["a.py"],
        affected_symbols=["A"],
    )
    assert result.failure["kind"] == "test"
    assert result.affected_files == ["a.py"]
    assert result.affected_symbols == ["A"]
