from __future__ import annotations
from .run import ExecutionRun, RunState

class ExecutionController:
    """Execution controller with optional durable run/event persistence."""

    def __init__(self, executor, persistence=None):
        self.executor = executor
        self.persistence = persistence
        self.runs: dict[str, ExecutionRun] = {}
        self._restore()

    def _restore(self):
        if self.persistence is None:
            return
        try:
            rows = self.persistence.repository.list_runs()
        except Exception:
            return
        for row in rows:
            payload = row.get("payload") or {}
            run_data = payload.get("run") if isinstance(payload, dict) else None
            if not isinstance(run_data, dict):
                continue
            try:
                run = ExecutionRun(
                    run_id=run_data.get("run_id", row["id"]),
                    request=run_data.get("request", ""),
                    state=RunState(run_data.get("state", row.get("state", "created"))),
                    results=run_data.get("results", []),
                    events=run_data.get("events", []),
                    created_at=run_data.get("created_at") or "",
                )
                self.runs[run.run_id] = run
            except Exception:
                continue

    def _persist(self, run):
        if self.persistence is None:
            return
        try:
            self.persistence.record_run(
                run.run_id,
                run.state.value,
                {"run": run.to_dict()},
                str(getattr(self.persistence, "workspace", "")) or None,
            )
        except Exception:
            # Runtime execution must not become unavailable solely because
            # the optional persistence backend is temporarily down.
            pass

    def _emit(self, run, event: str, **data):
        item = run.emit(event, **data)
        if self.persistence is not None:
            try:
                self.persistence.record_event(event, item, run.run_id)
            except Exception:
                pass
        self._persist(run)
        return item

    def create(self, request: str):
        run = ExecutionRun(request=request)
        self.runs[run.run_id] = run
        self._emit(run, "execution.created")
        return run

    def get(self, run_id):
        return self.runs.get(run_id)

    def cancel(self, run_id):
        run = self.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.state in {RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED}:
            return run
        run.state = RunState.CANCELLED
        self._emit(run, "execution.cancelled")
        return run

    def pause(self, run_id):
        run = self.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.state == RunState.RUNNING:
            run.state = RunState.PAUSED
            self._emit(run, "execution.paused")
        return run

    def execute(self, run_id, plan, context=None):
        run = self.get(run_id)
        if run is None:
            raise KeyError(run_id)
        if run.state == RunState.CANCELLED:
            return run

        run.state = RunState.RUNNING
        self._emit(run, "execution.started")

        for step in plan.steps:
            if run.state in {RunState.CANCELLED, RunState.PAUSED}:
                break

            self._emit(run, "execution.step.started", step_id=step.id)
            result = self.executor.execute_step(step, context or {})
            run.results.append(result.to_dict())
            self._emit(
                run,
                "execution.step.completed" if result.success else "execution.step.failed",
                step_id=step.id,
                result=result.to_dict(),
            )

            if result.state.value == "waiting_approval":
                run.state = RunState.WAITING_APPROVAL
                self._emit(run, "execution.waiting_approval", step_id=step.id)
                break

            if not result.success:
                run.state = RunState.FAILED
                self._emit(run, "execution.failed", step_id=step.id)
                break

        if run.state == RunState.RUNNING:
            run.state = RunState.COMPLETED
            self._emit(run, "execution.completed")
        else:
            self._persist(run)
        return run
