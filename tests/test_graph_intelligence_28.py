from pathlib import Path
from berkios.graph.intelligence import ProjectGraphIntelligence

def test_impact(tmp_path: Path):
    (tmp_path / "a.py").write_text("import b\nclass A: pass\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("class B: pass\n", encoding="utf-8")
    intelligence = ProjectGraphIntelligence(tmp_path)
    report = intelligence.impact("file:a.py", depth=2)
    assert report.target == "file:a.py"
    assert "a.py" in report.affected_files
