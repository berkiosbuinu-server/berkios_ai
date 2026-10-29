from __future__ import annotations

from typing import Any

from berkios.actionplan.models import (
    ActionKind,
    ActionPlan,
    PlannedAction,
)
from berkios.execution.models import (
    ExecutionPlan,
    ExecutionState,
    ExecutionStep,
)


def _action_plan_from_dict(data: dict[str, Any]) -> ActionPlan:
    actions = []

    for raw in data.get("actions", []):
        kind = raw.get("kind", "analyze")

        try:
            kind = ActionKind(kind)
        except ValueError:
            kind = ActionKind.ANALYZE

        actions.append(
            PlannedAction(
                id=raw["id"],
                kind=kind,
                description=raw.get(
                    "description",
                    "",
                ),
                capability=raw.get("capability"),
                tool=raw.get("tool"),
                target=raw.get("target"),
                requires_approval=bool(
                    raw.get(
                        "requires_approval",
                        False,
                    )
                ),
                requires_verification=bool(
                    raw.get(
                        "requires_verification",
                        False,
                    )
                ),
                risk=raw.get(
                    "risk",
                    "low",
                ),
                depends_on=list(
                    raw.get(
                        "depends_on",
                        [],
                    )
                ),
                metadata=dict(
                    raw.get(
                        "metadata",
                        {},
                    )
                ),
            )
        )

    return ActionPlan(
        request=data.get(
            "request",
            "",
        ),
        objective=data.get(
            "objective",
            "",
        ),
        actions=actions,
        risks=list(
            data.get(
                "risks",
                [],
            )
        ),
        assumptions=list(
            data.get(
                "assumptions",
                [],
            )
        ),
        approval_required=bool(
            data.get(
                "approval_required",
                False,
            )
        ),
        verification_required=bool(
            data.get(
                "verification_required",
                True,
            )
        ),
        rationale=data.get(
            "rationale",
            "",
        ),
    )


def _execution_plan_from_dict(
    data: dict[str, Any],
) -> ExecutionPlan:
    steps = []

    for raw in data.get("steps", []):
        state = raw.get(
            "state",
            ExecutionState.BLOCKED.value,
        )

        try:
            state = ExecutionState(state)
        except ValueError:
            state = ExecutionState.BLOCKED

        steps.append(
            ExecutionStep(
                id=raw["id"],
                action_id=raw.get(
                    "action_id",
                    raw["id"],
                ),
                capability=raw.get(
                    "capability"
                ),
                state=state,
                depends_on=list(
                    raw.get(
                        "depends_on",
                        [],
                    )
                ),
                requires_approval=bool(
                    raw.get(
                        "requires_approval",
                        False,
                    )
                ),
                requires_verification=bool(
                    raw.get(
                        "requires_verification",
                        False,
                    )
                ),
                tool=raw.get("tool"),
                target=raw.get("target"),
                reason=raw.get(
                    "reason",
                    "",
                ),
                metadata=dict(
                    raw.get(
                        "metadata",
                        {},
                    )
                ),
            )
        )

    return ExecutionPlan(
        request=data.get(
            "request",
            "",
        ),
        steps=steps,
        blocked_reasons=list(
            data.get(
                "blocked_reasons",
                [],
            )
        ),
    )


def build_job_handlers(runtime):
    """
    Construit les handlers officiels du worker.

    Aucun handler de test arbitraire n'est ajouté.
    """

    def agent_run(job):
        payload = job.payload or {}

        request = payload.get(
            "request",
            "",
        )

        run_id = payload.get(
            "run_id"
        )

        context = dict(
            payload.get(
                "context",
                {},
            )
        )

        agent = runtime.create_provider_agent()

        return agent.loop(
            request,
            run_id=run_id,
            **context,
        )

    def execution_run(job):
        payload = job.payload or {}

        run_id = payload.get("run_id")

        if not run_id:
            raise ValueError(
                "execution.run nécessite run_id"
            )

        plan_data = payload.get("plan")

        if not isinstance(plan_data, dict):
            raise ValueError(
                "execution.run nécessite plan"
            )

        execution_plan = _execution_plan_from_dict(
            plan_data
        )

        context = dict(
            payload.get(
                "context",
                {},
            )
        )

        controller = (
            runtime
            .create_execution_control()
            .controller
        )

        run = controller.get(run_id)

        if run is None:
            raise KeyError(
                f"ExecutionRun introuvable: {run_id}"
            )

        result = controller.execute(
            run_id,
            execution_plan,
            context,
        )

        return result.to_dict()

    def execution_resume(job):
        payload = job.payload or {}

        run_id = payload.get("run_id")

        if not run_id:
            raise ValueError(
                "execution.resume nécessite run_id"
            )

        controller = (
            runtime
            .create_execution_control()
            .controller
        )

        run = controller.get(run_id)

        if run is None:
            raise KeyError(
                f"ExecutionRun introuvable: {run_id}"
            )

        plan_data = payload.get("plan")

        if not isinstance(plan_data, dict):
            plan_data = run.plan

        if not isinstance(plan_data, dict):
            raise ValueError(
                "Aucun plan persistant disponible pour la reprise"
            )

        execution_plan = _execution_plan_from_dict(
            plan_data
        )

        context = dict(
            payload.get(
                "context",
                run.context or {},
            )
        )

        # Informations internes de reprise.
        # Elles ne doivent pas dépendre du contexte fourni par l'utilisateur.
        context["_execution_run_id"] = run.run_id

        approval_id = payload.get(
            "approval_id"
        )

        if approval_id:
            context["approval_id"] = approval_id

        result = (
            runtime
            .create_execution_resumer()
            .resume(
                run,
                execution_plan,
                context,
            )
        )

        return result.to_dict()

    return {
        "agent.run": agent_run,
        "execution.run": execution_run,
        "execution.resume": execution_resume,
    }
