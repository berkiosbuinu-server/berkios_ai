import tempfile
from pathlib import Path
from berkios.codeexplainer import CodeExplainer

def test_file():
    with tempfile.TemporaryDirectory() as d:
        Path(d,"app.py").write_text("import json\n\ndef hello(name):\n    return json.dumps(name)\n",encoding="utf-8")
        r=CodeExplainer(d).explain_file("app.py")
        assert "json" in r.dependencies and "hello" in r.symbols and r.connections

def test_symbol():
    with tempfile.TemporaryDirectory() as d:
        Path(d,"app.py").write_text("class Service:\n    def run(self):\n        return 1\n",encoding="utf-8")
        r=CodeExplainer(d).explain_symbol("app.py","Service")
        assert "Service" in r.target
