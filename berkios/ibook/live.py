from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class LiveRunSnapshot:
    run_id: str
    state: str
    request: str
    current_step: str | None
    results_count: int
    event_count: int
    last_event: dict[str, Any] | None

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "state": self.state,
            "request": self.request,
            "current_step": self.current_step,
            "results_count": self.results_count,
            "event_count": self.event_count,
            "last_event": self.last_event,
        }


class IBookLiveBridge:
    """Adaptateur minimal pour exposer l'état d'un run à iBook."""

    def __init__(self, controller):
        self.controller = controller

    def snapshot(self, run_id: str) -> LiveRunSnapshot:
        run = self.controller.get(run_id)
        if run is None:
            raise KeyError(run_id)

        current = None
        for event in reversed(run.events):
            if event["event"] == "execution.step.started":
                current = event["data"].get("step_id")
                break

        return LiveRunSnapshot(
            run_id=run.run_id,
            state=run.state.value,
            request=run.request,
            current_step=current,
            results_count=len(run.results),
            event_count=len(run.events),
            last_event=run.events[-1] if run.events else None,
        )

    def events(self, run_id: str, after: int = 0):
        run = self.controller.get(run_id)
        if run is None:
            raise KeyError(run_id)
        return run.events[after:]

    def pause(self, run_id: str):
        return self.controller.pause(run_id)

    def cancel(self, run_id: str):
        return self.controller.cancel(run_id)
