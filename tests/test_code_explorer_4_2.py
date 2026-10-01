from pathlib import Path
import tempfile
from berkios.codeexplorer import CodeExplorer

def test_symbol_connections():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        (root/"service.py").write_text(
            "def run():\n    return 1\n",encoding="utf-8")
        (root/"app.py").write_text(
            "from service import run\n\ndef main():\n    return run()\n",encoding="utf-8")
        r=CodeExplorer(root).explore_symbol("service.py","run")
        assert r.used_by
        assert any(x.file=="app.py" for x in r.used_by)
