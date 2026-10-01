from pathlib import Path
import ast
from collections import defaultdict, deque
from .models import GraphImpact, GraphPath

class CodeGraphIntelligence:
    """Construit un graphe Python léger et calcule l'impact direct/indirect."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()
        self.graph=defaultdict(set)
        self.reverse=defaultdict(set)
        self._build()

    def _build(self):
        for file in self.workspace.rglob("*.py"):
            if ".berkios" in file.parts or ".git" in file.parts:
                continue
            rel=str(file.relative_to(self.workspace))
            try:
                tree=ast.parse(file.read_text(encoding="utf-8",errors="replace"))
            except SyntaxError:
                continue
            module=self._module_name(file)
            self.graph[rel].add(module)
            self.reverse[module].add(rel)

            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    for a in node.names:
                        self.graph[rel].add(a.name)
                        self.reverse[a.name].add(rel)
                elif isinstance(node,ast.ImportFrom) and node.module:
                    self.graph[rel].add(node.module)
                    self.reverse[node.module].add(rel)

    def impact(self, target):
        target_path=str(target)
        module=self._module_from_target(target_path)
        direct=set(self.reverse.get(module,set()))
        direct.discard(target_path)

        indirect=set()
        paths=[]
        queue=deque([(x,[target_path,x]) for x in direct])
        seen=set(direct)

        while queue:
            node,path=queue.popleft()
            for nxt in self.reverse.get(self._module_name_from_rel(node),set()):
                if nxt==target_path or nxt in seen:
                    continue
                seen.add(nxt)
                indirect.add(nxt)
                paths.append((path+[nxt]))
                queue.append((nxt,path+[nxt]))

        deps=sorted(self.graph.get(target_path,set()))
        graph_paths=[__import__("berkios.codegraph.models",fromlist=["GraphPath"]).GraphPath(
            nodes=p,relation="depends-on",description="Chaîne de dépendance détectée."
        ) for p in paths[:50]]

        if len(indirect)>10 or len(direct)>5:
            risk="high"
        elif direct or indirect:
            risk="medium"
        else:
            risk="low"

        explanation=(
            f"{target_path} possède {len(direct)} dépendance(s) directe(s) "
            f"et {len(indirect)} dépendance(s) indirecte(s)."
        )

        return GraphImpact(
            target=target_path,
            direct_dependents=sorted(direct),
            indirect_dependents=sorted(indirect),
            dependencies=deps,
            paths=graph_paths,
            risk_level=risk,
            explanation=explanation,
        )

    def _module_name(self,file):
        try:
            rel=file.relative_to(self.workspace).with_suffix("")
            return ".".join(rel.parts)
        except ValueError:
            return file.stem

    def _module_from_target(self,target):
        p=Path(target)
        return ".".join(p.with_suffix("").parts)

    def _module_name_from_rel(self,rel):
        return self._module_name(self.workspace/rel)
