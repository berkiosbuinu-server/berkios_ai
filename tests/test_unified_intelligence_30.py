from pathlib import Path
from berkios.intelligence.unified import UnifiedIntelligence

def test_unified_snapshot(tmp_path: Path):
    (tmp_path / "a.py").write_text("import b\nclass A: pass\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("class B: pass\n", encoding="utf-8")
    snapshot = UnifiedIntelligence(tmp_path).build(
        "modify A",
        active_file="a.py",
        target_nodes=["file:a.py"],
    )
    assert snapshot.request == "modify A"
    assert snapshot.active_file == "a.py"
    assert "a.py" in snapshot.affected_files
