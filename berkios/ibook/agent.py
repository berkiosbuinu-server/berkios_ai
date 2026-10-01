from __future__ import annotations
from berkios.sdk.live import IBookAgentClient


class IBookAgentBridge:
    """Façade orientée éditeur pour iBook."""

    def __init__(self, base_url="http://127.0.0.1:8765"):
        self.client = IBookAgentClient(base_url)

    def ask(self, request, active_file=None, selection=None, **extra):
        payload = {}
        if active_file is not None:
            payload["active_file"] = active_file
        if selection is not None:
            payload["selection"] = selection
        payload.update(extra)
        return self.client.run(request, **payload)

    def status(self, run_id):
        return self.client.live_snapshot(run_id)

    def events(self, run_id, after=0):
        return self.client.live_events(run_id, after)

    def pause(self, run_id):
        return self.client.pause(run_id)

    def cancel(self, run_id):
        return self.client.cancel(run_id)
