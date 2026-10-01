import tempfile
from pathlib import Path
from berkios.contextfusion import ProjectContextFusion

class U:
    def analyze(self):
        return type("R",(),{"to_dict":lambda s:{"summary":"project"}})()

class E:
    def explain_file(self,p):
        return type("R",(),{"to_dict":lambda s:{"purpose":"role"}})()

def test_fusion():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); (p/"app.py").write_text("x=1\n",encoding="utf-8")
        f=ProjectContextFusion(p,project_understanding=U(),explainer=E())
        s=f.build(request="explain",target="app.py",active_file="app.py")
        assert s.project_understanding["summary"]=="project"
        assert "Rôle : role" in s.summary
