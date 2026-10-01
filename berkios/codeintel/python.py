import ast
from .models import Symbol, FileAnalysis

class PythonAnalyzer:
    def analyze(self, path, source):
        tree = ast.parse(source, filename=path)
        result = FileAnalysis(path, "python", lines=len(source.splitlines()))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                result.imports.extend(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                result.imports.append(node.module or "")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.symbols.append(Symbol(node.name, "function", path, node.lineno, node.col_offset))
            elif isinstance(node, ast.ClassDef):
                result.symbols.append(Symbol(node.name, "class", path, node.lineno, node.col_offset))
        return result
