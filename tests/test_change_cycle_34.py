from pathlib import Path
from berkios.runtime.change_cycle import ChangeCycle

class FakeChanges:
    def apply(self, proposal):
        return {"ok": True, "files": proposal.get("files", [])}

class FakeVerification:
    def verify(self):
        return {"ok": False, "error": "test failure"}

def test_change_cycle(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    cycle = ChangeCycle(
        tmp_path,
        changes=FakeChanges(),
        verification=FakeVerification(),
    )
    run = cycle.start("modify A")
    proposal = cycle.propose(run.run_id, {"files": ["a.py"]})
    applied = cycle.apply(run.run_id, proposal)
    assert applied["ok"]
    verification = cycle.verify(run.run_id)
    result = cycle.finish(run.run_id, verification)
    assert result.status == "repair_required"
    assert result.repair is not None
