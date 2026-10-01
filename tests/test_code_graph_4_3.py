from pathlib import Path
import tempfile
from berkios.codegraph import CodeGraphIntelligence

def test_impact_graph():
    with tempfile.TemporaryDirectory() as d:
        r=Path(d)
        (r/"base.py").write_text("def run(): return 1\n",encoding="utf-8")
        (r/"mid.py").write_text("from base import run\n",encoding="utf-8")
        (r/"app.py").write_text("from mid import run\n",encoding="utf-8")
        g=CodeGraphIntelligence(r)
        impact=g.impact("base.py")
        assert impact.risk_level in ("low","medium","high")
        assert impact.direct_dependents or impact.indirect_dependents
