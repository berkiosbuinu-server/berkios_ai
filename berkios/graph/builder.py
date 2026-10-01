from __future__ import annotations
import ast
from pathlib import Path
from .models import GraphNode, GraphEdge, ProjectGraph

class ProjectGraphBuilder:
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.graph = ProjectGraph(self.workspace)

    def build(self) -> ProjectGraph:
        self.graph = ProjectGraph(self.workspace)
        for path in self.workspace.rglob("*.py"):
            if ".berkios" in path.parts or "__pycache__" in path.parts:
                continue
            self._file(path)
        self.graph.save()
        return self.graph

    def _file(self, path: Path) -> None:
        rel = path.relative_to(self.workspace).as_posix()
        fid = f"file:{rel}"
        self.graph.add_node(GraphNode(fid, "file", rel, {"path": rel}))
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            return

        symbols = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                sid = f"symbol:{rel}:{node.name}:{node.lineno}"
                symbols[node.name] = sid
                self.graph.add_node(GraphNode(
                    sid, "symbol", node.name,
                    {"file": rel, "line": node.lineno, "symbol_type": type(node).__name__}
                ))
                self.graph.add_edge(GraphEdge(fid, sid, "defines"))

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._import(fid, alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._import(fid, node.module)

    def _import(self, source_id: str, module: str) -> None:
        module_id = f"module:{module}"
        self.graph.add_node(GraphNode(module_id, "module", module))
        self.graph.add_edge(GraphEdge(source_id, module_id, "imports"))
