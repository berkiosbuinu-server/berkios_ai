from pathlib import Path
from berkios.runtime.orchestrator import RuntimeOrchestrator

def test_orchestration(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    runtime = RuntimeOrchestrator(tmp_path)
    run = runtime.start("modify A", active_file="a.py",
                        target_nodes=["file:a.py"])
    proposal = runtime.propose_change(run.run_id, {"files": ["a.py"]})
    assert proposal.ok
    permission = runtime.request_permission(
        run.run_id, "file.write", "a.py"
    )
    assert permission.stage == "waiting_approval"
    result = runtime.verify(run.run_id, {"ok": True})
    assert result.stage == "completed"
