from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from .models import ApprovalDecision


@dataclass
class ApprovalBinding:
    approval_id: str
    run_id: str | None
    step_id: str | None
    action_id: str | None


class ApprovalExecutionBridge:
    """Lie une approbation à une étape précise d'un run."""

    def __init__(self, approval_manager, execution_controller):
        self.approvals = approval_manager
        self.execution = execution_controller
        self.bindings: dict[str, ApprovalBinding] = {}

    def bind(self, request, step_id: str | None = None):
        binding = ApprovalBinding(
            approval_id=request.approval_id,
            run_id=request.run_id,
            step_id=step_id,
            action_id=request.action_id,
        )
        self.bindings[request.approval_id] = binding
        return binding

    def decide(self, approval_id: str, approved: bool):
        request = (
            self.approvals.approve(approval_id)
            if approved else self.approvals.reject(approval_id)
        )
        binding = self.bindings.get(approval_id)
        if binding and binding.run_id:
            run = self.execution.get(binding.run_id)
            if run:
                event = (
                    "approval.approved" if approved
                    else "approval.rejected"
                )
                run.emit(
                    event,
                    approval_id=approval_id,
                    step_id=binding.step_id,
                    action_id=binding.action_id,
                )
        return request

    def is_approved(self, approval_id: str) -> bool:
        request = self.approvals.get(approval_id)
        return bool(
            request and request.decision == ApprovalDecision.APPROVED
        )
