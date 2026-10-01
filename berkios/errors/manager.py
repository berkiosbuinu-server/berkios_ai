from .parser import ErrorParser
from .analyzer import ErrorAnalyzer

class ErrorManager:
    def __init__(self, history=None, correction_memory=None):
        self.parser = ErrorParser()
        self.analyzer = ErrorAnalyzer()
        self.events = []
        self.diagnoses = {}
        self.history = history
        self.correction_memory = correction_memory

    def ingest_python(self, text, source="python"):
        events = self.parser.parse_python(text, source)
        return self._store(events)

    def ingest_command(self, argv, returncode, stdout="", stderr="", source="command"):
        events = self.parser.parse_command_result(argv, returncode, stdout, stderr, source)
        return self._store(events)

    def _store(self, events):
        for event in events:
            self.events.append(event)
            diagnosis = self.analyzer.analyze(event)
            self.diagnoses[event.id] = diagnosis
            if self.history is not None:
                try:
                    self.history.remember(event, diagnosis.to_dict())
                except Exception:
                    # Preserve error ingestion if optional persistence fails.
                    pass
        return events

    def list(self):
        return [e.to_dict() for e in self.events]

    def diagnose(self, error_id):
        return self.diagnoses[error_id].to_dict()

    def analyze(self, error_id):
        return self.diagnoses[error_id].to_dict()

    def latest(self):
        return self.events[-1].to_dict() if self.events else None
