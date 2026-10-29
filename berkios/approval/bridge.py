from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ApprovalBinding:
    approval_id: str
    run_id: str | None
    step_id: str | None
    action_id: str | None


class ApprovalExecutionBridge:
    """
    Relie une approbation à une exécution durable.

    Une approbation validée ne tente pas d'exécuter directement
    l'étape depuis le processus API.

    Elle remet un job execution.resume dans Redis/PostgreSQL.
    """

    def __init__(
        self,
        approval_manager,
        execution_controller,
        runtime=None,
    ):
        self.approvals = approval_manager
        self.execution = execution_controller
        self.runtime = runtime
        self.bindings = {}

    def bind(
        self,
        request,
        step_id=None,
    ):
        binding = ApprovalBinding(
            approval_id=request.approval_id,
            run_id=request.run_id,
            step_id=step_id,
            action_id=request.action_id,
        )

        self.bindings[
            request.approval_id
        ] = binding

        return binding

    def decide(
        self,
        approval_id,
        approved,
    ):
        request = (
            self.approvals.approve(
                approval_id
            )
            if approved
            else self.approvals.reject(
                approval_id
            )
        )

        binding = self.bindings.get(
            approval_id
        )

        # Le binding mémoire peut avoir disparu après un redémarrage
        # du processus API. Dans ce cas, reconstruire le binding
        # directement depuis l'approbation persistée.
        if binding is None and request is not None:
            metadata = getattr(request, "metadata", None) or {}

            binding = ApprovalBinding(
                approval_id=request.approval_id,
                run_id=getattr(request, "run_id", None)
                or metadata.get("run_id"),
                step_id=metadata.get("step_id"),
                action_id=getattr(request, "action_id", None)
                or metadata.get("action_id"),
            )

            self.bindings[approval_id] = binding

        if binding and binding.run_id:
            run = self.execution.get(
                binding.run_id
            )

            if run:
                event = (
                    "approval.approved"
                    if approved
                    else "approval.rejected"
                )

                run.emit(
                    event,
                    approval_id=approval_id,
                    step_id=binding.step_id,
                    action_id=binding.action_id,
                )

                if approved and self.runtime is not None:
                    queue = (
                        self.runtime
                        .create_job_queue()
                    )

                    queue.enqueue(
                        "execution.resume",
                        {
                            "run_id": binding.run_id,
                            "plan": run.plan,
                            "context": run.context,
                            "approval_id": approval_id,
                        },
                    )

                elif not approved:
                    run.state = (
                        type(run.state).FAILED
                    )

                try:
                    self.execution._persist(
                        run
                    )
                except Exception:
                    pass

        return request

    def is_approved(
        self,
        approval_id,
    ):
        request = self.approvals.get(
            approval_id
        )

        if request is None:
            return False

        from .models import ApprovalDecision

        return (
            request.decision
            == ApprovalDecision.APPROVED
        )
