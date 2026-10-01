class CodeIntelligence:
    def __init__(self, workspace, code_index, error_manager):
        from .correlator import ErrorCorrelator
        self.workspace, self.index, self.errors = workspace, code_index, error_manager
        self.correlator = ErrorCorrelator(workspace, code_index)

    def analyze_error(self, error_id):
        event = next(e for e in self.errors.events if e.id == error_id)
        return {"error": event.to_dict(),
                "diagnosis": self.errors.analyze(error_id),
                "correlation": self.correlator.correlate(event)}

    def project(self):
        return self.index.index_workspace()
