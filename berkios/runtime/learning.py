from __future__ import annotations

from berkios.learning.corrections import SelfLearningCorrectionLoop


class RuntimeLearning:
    """Runtime-facing façade for validated correction capture."""

    def __init__(self, workspace, correction_memory=None, event_sink=None):
        self.loop = SelfLearningCorrectionLoop(
            workspace,
            correction_memory=correction_memory,
            event_sink=event_sink,
        )

    def capture_verified_repair(self, **kwargs):
        return self.loop.capture(**kwargs)

    def relevant_corrections(self, **kwargs):
        return self.loop.relevant(**kwargs)
