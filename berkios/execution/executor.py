from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable
import time

from .models import ExecutionPlan, ExecutionState


@dataclass
class ToolResult:
    step_id: str
    success: bool
    state: ExecutionState
    output: Any = None
    error: str | None = None
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "success": self.success,
            "state": self.state.value,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class ToolExecutor:
    """Exécute des capacités enregistrées, sans contourner les approvals."""

    def __init__(self, handlers=None, permission_checker=None):
        self.handlers = handlers or {}
        self.permission_checker = permission_checker

    def register(self, capability: str, handler: Callable[..., Any]):
        self.handlers[capability] = handler

    def _allowed(self, step) -> bool:
        if self.permission_checker is None:
            return not step.requires_approval
        try:
            return bool(self.permission_checker(step.capability))
        except Exception:
            return False

    def execute_step(self, step, context=None):
        context = context or {}
        started = time.perf_counter()

        if step.state == ExecutionState.BLOCKED:
            return ToolResult(
                step.id, False, ExecutionState.BLOCKED,
                error=step.reason or "étape bloquée"
            )

        if step.state == ExecutionState.WAITING_APPROVAL:
            return ToolResult(
                step.id, False, ExecutionState.WAITING_APPROVAL,
                error="approbation explicite requise"
            )

        handler = self.handlers.get(step.capability)
        if handler is None:
            return ToolResult(
                step.id, False, ExecutionState.FAILED,
                error=f"aucun handler pour {step.capability}"
            )

        if not self._allowed(step):
            return ToolResult(
                step.id, False, ExecutionState.WAITING_APPROVAL,
                error="permission refusée ou non accordée"
            )

        try:
            output = handler(step=step, context=context)
            duration = int((time.perf_counter() - started) * 1000)
            return ToolResult(
                step.id, True, ExecutionState.COMPLETED,
                output=output, duration_ms=duration
            )
        except Exception as exc:
            duration = int((time.perf_counter() - started) * 1000)
            return ToolResult(
                step.id, False, ExecutionState.FAILED,
                error=str(exc), duration_ms=duration
            )

    def execute_ready(self, plan: ExecutionPlan, context=None):
        context = context or {}
        results = []
        completed = set()

        for step in plan.steps:
            if any(dep not in completed for dep in step.depends_on):
                if step.state == ExecutionState.READY:
                    step.state = ExecutionState.BLOCKED
                    step.reason = "dépendance non exécutée"
            result = self.execute_step(step, context)
            results.append(result)
            if result.success:
                completed.add(step.id)
        return results
