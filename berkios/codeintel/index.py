from pathlib import Path
from .python import PythonAnalyzer

class CodeIndex:
    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve()
        self.files = {}
        self.python = PythonAnalyzer()

    def index_file(self, relative_path):
        path = (self.workspace / relative_path).resolve()
        if self.workspace not in path.parents and path != self.workspace:
            raise ValueError("Outside workspace")
        source = path.read_text(encoding="utf-8")
        analysis = self.python.analyze(relative_path, source) if path.suffix == ".py" else {
            "path": relative_path, "language": path.suffix.lstrip(".") or "text",
            "lines": len(source.splitlines()), "symbols": [], "imports": []
        }
        self.files[relative_path] = analysis
        return analysis

    def index_workspace(self):
        for p in self.workspace.rglob("*.py"):
            if ".berkios" not in p.parts:
                self.index_file(str(p.relative_to(self.workspace)))
        return self.snapshot()

    def find_symbol(self, name):
        hits = []
        for item in self.files.values():
            data = item.to_dict() if hasattr(item, "to_dict") else item
            for symbol in data.get("symbols", []):
                if symbol["name"] == name: hits.append({"file": data["path"], **symbol})
        return hits

    def snapshot(self):
        return {k: (v.to_dict() if hasattr(v, "to_dict") else v) for k,v in self.files.items()}
