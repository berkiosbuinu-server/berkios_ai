from __future__ import annotations
from berkios.ibook.live import IBookLiveBridge

class RuntimeLiveBridge:
    def __init__(self, runtime):
        self.runtime = runtime
        self.bridge = IBookLiveBridge(runtime.create_execution_control().controller)

    def snapshot(self, run_id):
        return self.bridge.snapshot(run_id)

    def events(self, run_id, after=0):
        local = self.bridge.events(run_id, after)
        if local:
            return local
        try:
            return self.runtime.create_persistence().repository.events_after(
                after, run_id=run_id
            )
        except Exception:
            return []

    def pause(self, run_id):
        return self.bridge.pause(run_id)

    def cancel(self, run_id):
        return self.bridge.cancel(run_id)
