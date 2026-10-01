from pathlib import Path
import ast
import json
from .models import ProjectComponent, ProjectUnderstanding

class ProjectUnderstandingEngine:
    """Construit une vue globale locale du projet pour le contexte Berkios."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()

    def analyze(self):
        components=[]
        languages=set()
        external=set()
        entries=[]
        flows=[]
        risks=[]

        py_files=[]
        for p in self.workspace.rglob("*.py"):
            if ".berkios" in p.parts or ".git" in p.parts:
                continue
            py_files.append(p)

        for p in py_files:
            rel=str(p.relative_to(self.workspace))
            languages.add("Python")
            try:
                source=p.read_text(encoding="utf-8",errors="replace")
                tree=ast.parse(source,filename=str(p))
            except SyntaxError:
                risks.append(f"Syntaxe invalide : {rel}")
                continue

            imports=[]
            symbols=[]
            has_main=False
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):
                    imports += [a.name for a in n.names]
                elif isinstance(n,ast.ImportFrom) and n.module:
                    imports.append(n.module)
                elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    symbols.append(n.name)
                elif isinstance(n,ast.Call):
                    if isinstance(n.func,ast.Name) and n.func.id=="main":
                        has_main=True

            imports=list(dict.fromkeys(imports))
            symbols=list(dict.fromkeys(symbols))

            role=self._role(rel,imports,symbols)
            if has_main or p.name in ("main.py","__main__.py","cli.py"):
                entries.append(rel)

            for dep in imports:
                if not dep.startswith("."):
                    external.add(dep.split(".")[0])

            components.append(ProjectComponent(
                name=p.stem,
                path=rel,
                kind="python_module",
                role=role,
                dependencies=imports,
                symbols=symbols[:100],
            ))

        # Common project entry points.
        for candidate in ("pyproject.toml","requirements.txt","setup.py","package.json","README.md"):
            if (self.workspace/candidate).exists():
                entries.append(candidate)

        entries=list(dict.fromkeys(entries))
        external=sorted(external)

        if len(components)>20:
            architecture.append if False else None

        architecture=[
            f"{len(components)} module(s) Python détecté(s).",
            f"{len(external)} dépendance(s) externes détectée(s).",
        ]
        if entries:
            architecture.append("Points d'entrée/configuration : "+", ".join(entries[:15]))

        if components:
            flows.append("Configuration/entrée → modules → dépendances externes.")
            flows.append("Les symboles exposés par les modules constituent les points de réutilisation internes.")

        summary=(
            f"Projet composé de {len(components)} module(s), "
            f"avec {len(external)} dépendance(s) externe(s)."
        )

        return ProjectUnderstanding(
            project_name=self.workspace.name,
            languages=sorted(languages),
            components=components,
            entry_points=entries,
            architecture=architecture,
            flows=flows,
            external_dependencies=external,
            risks=risks,
            summary=summary,
            confidence=min(0.95,0.4+0.03*min(len(components),15)),
        )

    def save(self, filename=".berkios/project_understanding.json"):
        result=self.analyze()
        p=self.workspace/filename
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result.to_dict(),indent=2,ensure_ascii=False),encoding="utf-8")
        return result

    def _role(self,path,imports,symbols):
        low=path.lower()
        if "test" in low: return "Tests et vérification."
        if "api" in low or any(x in imports for x in ("fastapi","flask","http")):
            return "Interface API ou réseau."
        if "cli" in low: return "Interface en ligne de commande."
        if "model" in low or "schema" in low: return "Modèles ou structures de données."
        if "service" in low: return "Service ou logique métier."
        if "util" in low or "helper" in low: return "Utilitaires."
        if symbols: return "Module de logique ou d'abstraction."
        return "Module de support."
