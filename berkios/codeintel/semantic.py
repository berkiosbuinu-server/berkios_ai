from pathlib import Path

class ProjectSemanticAnalyzer:
    def __init__(self, workspace, code_index):
        self.workspace=Path(workspace).resolve()
        self.index=code_index

    def build_relations(self):
        relations=[]
        for path,data in self.index.snapshot().items():
            for module in data.get("imports",[]):
                relations.append({
                    "type":"dependency",
                    "from":path,
                    "to":module,
                    "reason":"python import"
                })
        return relations

    def summarize(self):
        snap=self.index.snapshot()
        return {
            "files":len(snap),
            "python_files":sum(1 for x in snap.values() if x.get("language")=="python"),
            "relations":self.build_relations()
        }
