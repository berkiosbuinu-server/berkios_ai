from berkios.intelligence.unified import UnifiedIntelligence

class IntelligenceRuntime:
    def __init__(self, workspace, runtime=None):
        self.engine = UnifiedIntelligence(workspace, runtime)

    def snapshot(self, request, **kwargs):
        return self.engine.build(request, **kwargs)
