from __future__ import annotations
import json
import urllib.request
import urllib.error


class IBookAgentClient:
    """SDK Python minimal pour piloter un run Berkios depuis iBook."""

    def __init__(self, base_url="http://127.0.0.1:8765"):
        self.base_url = base_url.rstrip("/")

    def _post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def live_snapshot(self, run_id):
        return self._post("/v1/live/runs", {"run_id": run_id})

    def live_events(self, run_id, after=0):
        return self._post(
            "/v1/live/events",
            {"run_id": run_id, "after": after},
        )

    def pause(self, run_id):
        return self._post("/v1/live/pause", {"run_id": run_id})

    def cancel(self, run_id):
        return self._post("/v1/live/cancel", {"run_id": run_id})

    def run(self, request, **context):
        return self._post("/v1/agent/run", {
            "request": request,
            **context,
        })

    def wait_events(self, run_id, after=0, max_polls=1):
        """Récupère les nouveaux événements sans créer de boucle infinie."""
        cursor = after
        batches = []
        for _ in range(max_polls):
            result = self.live_events(run_id, cursor)
            events = result.get("events", [])
            batches.extend(events)
            cursor += len(events)
        return {
            "run_id": run_id,
            "after": after,
            "next": cursor,
            "events": batches,
        }
