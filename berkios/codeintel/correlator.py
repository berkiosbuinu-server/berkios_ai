from pathlib import Path

class ErrorCorrelator:
    def __init__(self, workspace, code_index):
        self.workspace = Path(workspace).resolve()
        self.index = code_index

    def correlate(self, error):
        result = {"error_id": error.id,
                  "location": {"file": error.file, "line": error.line, "column": error.column},
                  "symbol": None, "file_analysis": None, "nearby_code": "", "imports": []}
        if not error.file: return result
        path = (self.workspace / error.file).resolve()
        if self.workspace not in path.parents and path != self.workspace: return result
        try:
            relative = path.relative_to(self.workspace).as_posix()
            analysis = (self.index.files.get(error.file) or self.index.files.get(relative)
                        or self.index.index_file(relative))
            data = analysis.to_dict() if hasattr(analysis, "to_dict") else analysis
            result["file_analysis"], result["imports"] = data, data.get("imports", [])
            if error.line:
                symbols = [s for s in data.get("symbols", []) if s["line"] <= error.line]
                if symbols: result["symbol"] = sorted(symbols, key=lambda x:x["line"])[-1]
                lines = path.read_text(encoding="utf-8").splitlines()
                start, end = max(0,error.line-4), min(len(lines),error.line+3)
                result["nearby_code"] = "\n".join(f"{i+1}: {lines[i]}" for i in range(start,end))
        except (OSError, SyntaxError, UnicodeDecodeError):
            pass
        return result
