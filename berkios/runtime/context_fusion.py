from berkios.contextfusion import ProjectContextFusion

class RuntimeContextFusion:
    def __init__(self,workspace,**components):
        self.fusion=ProjectContextFusion(workspace,**components)
    def build(self,**kwargs):
        return self.fusion.build(**kwargs).to_dict()
