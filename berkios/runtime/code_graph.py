from berkios.codegraph import CodeGraphIntelligence

class RuntimeCodeGraph:
    def __init__(self,workspace):
        self.engine=CodeGraphIntelligence(workspace)
    def impact(self,target):
        return self.engine.impact(target).to_dict()
