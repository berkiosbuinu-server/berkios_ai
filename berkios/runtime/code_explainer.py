from berkios.codeexplainer import CodeExplainer
class RuntimeCodeExplainer:
    def __init__(self,workspace): self.engine=CodeExplainer(workspace)
    def explain_file(self,path): return self.engine.explain_file(path).to_dict()
    def explain_symbol(self,path,symbol): return self.engine.explain_symbol(path,symbol).to_dict()
    def explain_selection(self,source,target="selection"): return self.engine.explain_selection(source,target).to_dict()
