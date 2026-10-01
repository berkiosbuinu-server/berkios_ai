from pathlib import Path
import tempfile
from berkios.changeintelligence import ChangeImpactPlanner

def test_plan_contains_verification():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        (r/"base.py").write_text("def run(): return 1\n",encoding="utf-8")
        (r/"app.py").write_text("from base import run\n",encoding="utf-8")
        plan=ChangeImpactPlanner(r).plan("base.py","modifier run")
        assert plan.approval_required is True
        assert plan.verification_targets
        assert "app.py" in plan.affected_files
