from pathlib import Path
from berkios.agent.impact import ImpactAwarePlanner

def test_impact_aware_plan(tmp_path: Path):
    (tmp_path / "a.py").write_text("import b\nclass A: pass\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("class B: pass\n", encoding="utf-8")
    planner = ImpactAwarePlanner(tmp_path)
    plan = planner.analyze_targets(["file:a.py"], "modify A")
    assert plan.targets == ["file:a.py"]
    assert "a.py" in plan.affected_files
