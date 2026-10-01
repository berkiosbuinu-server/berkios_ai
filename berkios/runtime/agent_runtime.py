from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from berkios.agent.run_context import AgentRunContext

class RuntimeState(str, Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    PROPOSING = "proposing"
    WAITING_APPROVAL = "waiting_approval"
    APPLYING = "applying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RuntimeRun:
    run_id: str
    request: str
    state: RuntimeState = RuntimeState.IDLE
    context: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def event(self, kind: str, **data):
        self.events.append({
            "kind": kind,
            "state": self.state.value,
            "data": data,
        })

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "request": self.request,
            "state": self.state.value,
            "context": self.context,
            "events": self.events,
        }

class AgentRuntime:
    """Canonical entry point for Berkios development runs."""

    def __init__(self, workspace, runtime=None, run_memory=None):
        self.workspace = workspace
        self.runtime = runtime
        self.run_memory = run_memory
        self.runs: dict[str, RuntimeRun] = {}
        self._counter = 0

    def start(self, request: str, *, active_file=None,
              selection=None, target_nodes=None) -> RuntimeRun:
        self._counter += 1
        run_id = f"run-{self._counter:06d}"
        run = RuntimeRun(run_id=run_id, request=request)
        self.runs[run_id] = run

        context = AgentRunContext(
            self.workspace,
            self.runtime,
            self.run_memory,
        )
        prepared = context.prepare(
            request,
            active_file=active_file,
            selection=selection,
            target_nodes=target_nodes or [],
        )

        run.context = prepared.snapshot
        run.state = RuntimeState.ANALYZING
        run.event(
            "run.started",
            intelligence_ready=True,
            affected_files=run.context.get("affected_files", []),
        )
        self._remember(run, "run.started")
        return run

    def transition(self, run_id: str, state: RuntimeState,
                   **detail) -> RuntimeRun:
        run = self.runs[run_id]
        run.state = RuntimeState(state)
        run.event("run.transition", **detail)
        self._remember(run, "run.transition")
        return run

    def record_decision(self, run_id: str, decision: dict[str, Any]):
        run = self.runs[run_id]
        run.event("agent.decision", decision=decision)
        self._remember(run, "agent.decision")
        return run

    def record_verification(self, run_id: str, result: dict[str, Any]):
        run = self.runs[run_id]
        run.state = RuntimeState.VERIFYING
        run.event("verification.result", result=result)
        self._remember(run, "verification.result")
        return run

    def complete(self, run_id: str, result: dict[str, Any] | None = None):
        run = self.runs[run_id]
        run.state = RuntimeState.COMPLETED
        run.event("run.completed", result=result or {})
        self._remember(run, "run.completed")
        return run

    def fail(self, run_id: str, error: str):
        run = self.runs[run_id]
        run.state = RuntimeState.FAILED
        run.event("run.failed", error=error)
        self._remember(run, "run.failed")
        return run

    def get(self, run_id: str) -> RuntimeRun:
        return self.runs[run_id]

    def list(self):
        return list(self.runs.values())

    def _remember(self, run, event_type):
        if self.run_memory is None:
            return
        payload = {
            "type": event_type,
            "run_id": run.run_id,
            "state": run.state.value,
        }
        for name in ("add", "remember", "record"):
            method = getattr(self.run_memory, name, None)
            if callable(method):
                try:
                    method(payload)
                    return
                except Exception:
                    pass


    def create_codix_teacher(self, root=".berkios/teacher_data"):
        from .codix_teacher import RuntimeCodixTeacher
        return RuntimeCodixTeacher(root)


    def create_codix_multi_teacher(self):
        from .codix_multi_teacher import RuntimeCodixMultiTeacher
        return RuntimeCodixMultiTeacher()


    def create_codix_dataset_factory(self, root=".berkios/datasets", seed=42):
        from .codix_dataset_factory import RuntimeCodixDatasetFactory
        return RuntimeCodixDatasetFactory(root=root, seed=seed)


    def create_codix_auto_training(self, root=".berkios/auto_training", config=None):
        from .codix_auto_training import RuntimeCodixAutoTraining
        return RuntimeCodixAutoTraining(root=root, config=config)


    def create_codix_trainer(self, root=".berkios/trainer_runs"):
        from .codix_trainer import RuntimeCodixTrainer
        return RuntimeCodixTrainer(root)


    def create_codix_local_ml(self):
        from .codix_local_ml import RuntimeCodixLocalML
        return RuntimeCodixLocalML()


    def create_codix_evaluation(self, root=".berkios/model_registry"):
        from .codix_evaluation import RuntimeCodixEvaluation
        return RuntimeCodixEvaluation(root)


    def create_codix_continuous(self, root=".berkios/continuous_learning", config=None):
        from .codix_continuous import RuntimeCodixContinuous
        return RuntimeCodixContinuous(root, config)

    def create_persistence(self, database_url=None, redis_url=None):
        from .persistence import RuntimePersistence
        return RuntimePersistence(database_url=database_url, redis_url=redis_url)
