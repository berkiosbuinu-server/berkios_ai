from pathlib import Path
import tempfile
from berkios.projectunderstanding import ProjectUnderstandingEngine

def test_project_understanding():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        (r/"main.py").write_text("from service import run\ndef main(): return run()\n",encoding="utf-8")
        (r/"service.py").write_text("def run(): return 1\n",encoding="utf-8")
        result=ProjectUnderstandingEngine(r).analyze()
        assert len(result.components)==2
        assert "Python" in result.languages
        assert result.entry_points
        assert result.summary
