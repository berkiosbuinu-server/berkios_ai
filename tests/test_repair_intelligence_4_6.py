import tempfile
from pathlib import Path
from berkios.repairintel import RepairIntelligence

def test_prepare_repair():
    with tempfile.TemporaryDirectory() as d:
        p=RepairIntelligence(Path(d)).prepare(
            "app.py","invalid syntax",error_kind="syntax",
            affected_files=["app.py"])
        assert p.approval_required
        assert p.likely_causes
        assert p.verification_steps
