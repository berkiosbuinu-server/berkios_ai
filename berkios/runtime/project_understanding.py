from berkios.projectunderstanding import ProjectUnderstandingEngine

class RuntimeProjectUnderstanding:
    def __init__(self,workspace):
        self.engine=ProjectUnderstandingEngine(workspace)
    def analyze(self):
        return self.engine.analyze().to_dict()
    def save(self):
        return self.engine.save().to_dict()
