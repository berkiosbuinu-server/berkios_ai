from pathlib import Path
import ast
from .models import CodeExplanation, CodeConnection

class CodeExplainer:
    """Analyse locale du code : rôle, usage, dépendances, appels et connexions."""
    def __init__(self, workspace):
        self.workspace=Path(workspace).resolve()

    def explain_file(self,path):
        p=(self.workspace/path).resolve()
        if not p.is_file(): raise FileNotFoundError(str(p))
        return self.explain_source(p.read_text(encoding="utf-8",errors="replace"),
                                   str(p.relative_to(self.workspace)))

    def explain_symbol(self,path,symbol):
        p=(self.workspace/path).resolve()
        source=p.read_text(encoding="utf-8",errors="replace")
        tree=ast.parse(source,filename=str(p))
        node=next((n for n in ast.walk(tree)
                   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))
                   and n.name==symbol),None)
        if node is None: raise ValueError(f"Symbol not found: {symbol}")
        segment=ast.get_source_segment(source,node) or ""
        r=self.explain_source(segment,f"{p.relative_to(self.workspace)}::{symbol}")
        r.target=f"{p.relative_to(self.workspace)}::{symbol}"
        r.summary=f"Explication du symbole « {symbol} »."
        r.purpose=ast.get_docstring(node) or (
            f"Définit la classe {symbol}." if isinstance(node,ast.ClassDef)
            else f"Définit la fonction {symbol}.")
        return r

    def explain_selection(self,source,target="selection"):
        return self.explain_source(source,target)

    def explain_source(self,source,target="<source>",language="python"):
        if language!="python":
            return CodeExplanation(target,language,"Analyse limitée",
                "Le contexte IA peut enrichir l'explication.",[],[],[],[],[],[],[],[],[],0.2)
        try:
            tree=ast.parse(source,filename=target)
        except SyntaxError as e:
            return CodeExplanation(target,"python","Erreur de syntaxe",
                "L'analyse complète est bloquée par la syntaxe.",[],[],[],[],[],[],
                [f"Ligne {e.lineno}: {e.msg}"],["Corriger la syntaxe puis relancer."],0.15)

        imports=[]; symbols=[]; calls=[]; inputs=[]; outputs=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import): imports += [a.name for a in n.names]
            elif isinstance(n,ast.ImportFrom) and n.module: imports.append(n.module)
            elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)): symbols.append(n.name)
            elif isinstance(n,ast.Call): calls.append(self._call(n))
            elif isinstance(n,ast.arg): inputs.append(n.arg)
            elif isinstance(n,ast.Return): outputs.append("valeur retournée")
        imports=list(dict.fromkeys(imports)); symbols=list(dict.fromkeys(symbols))
        calls=[x for x in dict.fromkeys(calls) if x]

        connections=[CodeConnection(target,d,"imports",f"{target} importe {d}.") for d in imports]
        connections += [CodeConnection(target,c,"calls",f"{target} appelle {c}.") for c in calls[:30]]

        flow=[]
        if imports: flow.append("Dépend de : "+", ".join(imports[:20]))
        if symbols: flow.append("Expose : "+", ".join(symbols[:20]))
        if calls: flow.append("Appelle : "+", ".join(calls[:20]))

        risks=[]; suggestions=[]
        if "subprocess" in imports:
            risks.append("Exécution de processus système détectée.")
            suggestions.append("Contrôler les commandes et privilégier shell=False.")
        if "eval" in calls or "exec" in calls: risks.append("Exécution dynamique détectée.")
        if not symbols: suggestions.append("Des fonctions/classes nommées faciliteraient la maintenance.")

        return CodeExplanation(
            target,"python",f"Analyse de {target}.",
            self._purpose(target,imports,symbols),
            ["Utiliser les symboles exposés par ce module."] if symbols
            else ["Consulter les références du projet pour identifier le point d'entrée."],
            list(dict.fromkeys(inputs))[:50],list(dict.fromkeys(outputs)),
            imports,symbols,connections,flow,risks,suggestions,
            min(.95,.45+.1*bool(symbols)+.1*bool(imports)+.1*bool(calls)))

    def _call(self,n):
        if isinstance(n.func,ast.Name): return n.func.id
        if isinstance(n.func,ast.Attribute):
            parts=[]; cur=n.func
            while isinstance(cur,ast.Attribute):
                parts.append(cur.attr); cur=cur.value
            if isinstance(cur,ast.Name): parts.append(cur.id)
            return ".".join(reversed(parts))
        return ""

    def _purpose(self,target,imports,symbols):
        low=target.lower()
        if "test" in low or "pytest" in " ".join(imports): return "Participe probablement aux tests."
        if "api" in low or any(x in imports for x in ("http","requests","fastapi")):
            return "Participe probablement à une interface API ou réseau."
        if symbols: return "Regroupe de la logique et des abstractions réutilisables."
        return "Contient une logique d'exécution ou de support du projet."
