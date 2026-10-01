from pathlib import Path
import ast
from .models import CodeRelation, CodeExplorerReport

class CodeExplorer:
    """Explore les connexions Python autour d'un fichier ou d'un symbole."""

    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()

    def explore_symbol(self, path, symbol):
        target_file=(self.workspace/path).resolve()
        definition=f"{target_file.relative_to(self.workspace)}::{symbol}"
        used_by=[]; uses=[]; imports=[]; imported_by=[]
        related=set()
        definition_line=None

        # Find the definition.
        for file in self._python_files():
            try:
                source=file.read_text(encoding="utf-8",errors="replace")
                tree=ast.parse(source,filename=str(file))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    if file==target_file and node.name==symbol:
                        definition_line=node.lineno
                        break

        # Search references throughout the project.
        for file in self._python_files():
            try:
                source=file.read_text(encoding="utf-8",errors="replace")
                tree=ast.parse(source,filename=str(file))
            except SyntaxError:
                continue

            rel=str(file.relative_to(self.workspace))
            for node in ast.walk(tree):
                if isinstance(node,ast.Name) and node.id==symbol:
                    if file!=target_file or node.lineno!=definition_line:
                        relation=CodeRelation(
                            source=rel,
                            target=definition,
                            kind="uses",
                            explanation=f"{rel} utilise {symbol}.",
                            file=rel,
                            line=node.lineno
                        )
                        used_by.append(relation)
                        related.add(rel)

                if isinstance(node,(ast.Import,ast.ImportFrom)):
                    text=ast.unparse(node)
                    if symbol in text:
                        imports.append(CodeRelation(
                            source=rel,target=definition,kind="imports",
                            explanation=f"{rel} importe ou référence {symbol}.",
                            file=rel,line=getattr(node,"lineno",None)
                        ))

        # Local calls made by the target symbol.
        try:
            source=target_file.read_text(encoding="utf-8",errors="replace")
            tree=ast.parse(source,filename=str(target_file))
            node=next((n for n in ast.walk(tree)
                       if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))
                       and n.name==symbol),None)
            if node:
                for call in ast.walk(node):
                    if isinstance(call,ast.Call):
                        name=self._call_name(call)
                        if name:
                            uses.append(CodeRelation(
                                source=definition,target=name,kind="calls",
                                explanation=f"{symbol} appelle {name}.",
                                file=str(target_file.relative_to(self.workspace)),
                                line=getattr(call,"lineno",None)
                            ))
        except (SyntaxError,FileNotFoundError):
            pass

        # Imported module relationships for the target file.
        try:
            tree=ast.parse(target_file.read_text(encoding="utf-8",errors="replace"))
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):
                    for alias in node.names:
                        imports.append(CodeRelation(
                            source=str(target_file.relative_to(self.workspace)),
                            target=alias.name,kind="imports",
                            explanation=f"Le fichier dépend de {alias.name}.",
                            file=str(target_file.relative_to(self.workspace)),
                            line=node.lineno
                        ))
                elif isinstance(node,ast.ImportFrom) and node.module:
                    imports.append(CodeRelation(
                        source=str(target_file.relative_to(self.workspace)),
                        target=node.module,kind="imports",
                        explanation=f"Le fichier dépend de {node.module}.",
                        file=str(target_file.relative_to(self.workspace)),
                        line=node.lineno
                    ))
        except SyntaxError:
            pass

        used_by=self._unique(used_by)
        uses=self._unique(uses)
        imports=self._unique(imports)
        imported_by=self._unique(imported_by)

        impact=[]
        if used_by:
            impact.append(f"{len(used_by)} référence(s) peuvent être affectées par une modification.")
        if uses:
            impact.append(f"{len(uses)} appel(s) doivent être vérifiés.")
        if not used_by:
            impact.append("Aucune utilisation directe détectée dans les fichiers Python analysés.")

        flow=[
            f"Définition : {definition}",
            f"Utilisé par : {len(used_by)} référence(s)",
            f"Utilise/appelle : {len(uses)} élément(s)",
            f"Dépend de : {len(imports)} élément(s)",
        ]

        why=self._why(symbol,used_by,uses,imports)
        examples=[
            f"Référence : {r.file}:{r.line}" for r in used_by[:10]
            if r.file and r.line
        ]

        return CodeExplorerReport(
            target=definition,
            definition=definition,
            used_by=used_by,
            uses=uses,
            imports=imports,
            imported_by=imported_by,
            related_files=sorted(related),
            impact=impact,
            flow=flow,
            why=why,
            usage_examples=examples,
        )

    def explore_file(self,path):
        p=(self.workspace/path).resolve()
        return self.explore_symbol(p.relative_to(self.workspace),"__file__")

    def _python_files(self):
        return [p for p in self.workspace.rglob("*.py")
                if ".berkios" not in p.parts and ".git" not in p.parts]

    def _call_name(self,node):
        if isinstance(node.func,ast.Name):
            return node.func.id
        if isinstance(node.func,ast.Attribute):
            return node.func.attr
        return ""

    def _unique(self,items):
        seen=set(); result=[]
        for x in items:
            key=(x.source,x.target,x.kind,x.line)
            if key not in seen:
                seen.add(key); result.append(x)
        return result

    def _why(self,symbol,used_by,uses,imports):
        if used_by and uses:
            return f"{symbol} est un élément connecté : il est utilisé par le projet et dépend lui-même d'autres éléments."
        if used_by:
            return f"{symbol} sert de point réutilisé par d'autres parties du projet."
        if uses:
            return f"{symbol} orchestre ou utilise d'autres éléments du projet."
        if imports:
            return f"{symbol} appartient à un fichier qui dépend de plusieurs composants."
        return f"{symbol} n'a pas de connexion directe détectée dans l'analyse actuelle."
