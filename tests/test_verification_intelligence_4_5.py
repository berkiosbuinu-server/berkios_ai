from pathlib import Path
import tempfile
from berkios.verificationintel import VerificationIntelligence

def test_inspection():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        (r/"app.py").write_text("def main():\n    return 1\n",encoding="utf-8")
        report=VerificationIntelligence(r).inspect_files("app.py",["app.py"])
        assert report.passed
        assert report.verified_targets == ["app.py"]

def test_syntax_failure():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        (r/"bad.py").write_text("def main(:\n",encoding="utf-8")
        report=VerificationIntelligence(r).inspect_files("bad.py",["bad.py"])
        assert not report.passed
        assert any(x.status=="failed" for x in report.findings)
