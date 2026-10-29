from __future__ import annotations

from typing import Any

from berkios.execution import ToolExecutor
from berkios.approval import ApprovalDecision


class RuntimeToolExecutor:
    """
    Pont entre le moteur d'exécution canonique et le ToolRegistry réel.

    Les approvals restent liées à une exécution précise :
        run_id
        step_id
        approval_id
        action_id
        capability

    Une approbation ne devient donc jamais une autorisation globale
    d'une capability.
    """

    INTERNAL_CAPABILITIES = {
        "context.read",
        "changes.propose",
        "verification.run",
        "code.explain",
    }

    def __init__(self, runtime):
        self.runtime = runtime
        self.registry = runtime.tools

        handlers = {}

        for name in getattr(
            self.registry,
            "tools",
            {},
        ):
            handlers[name] = (
                self._make_tool_handler(name)
            )

        for capability in self.INTERNAL_CAPABILITIES:
            handlers[capability] = (
                self._make_internal_handler(
                    capability
                )
            )

        self.executor = ToolExecutor(
            handlers=handlers,
            permission_checker=(
                self._permission_checker
            ),
            approval_checker=(
                self._approval_checker
            ),
        )

    def _permission_checker(
        self,
        capability,
    ):
        """
        Permission technique uniquement.

        Cette méthode ne valide jamais une approbation métier.
        """

        if capability in self.INTERNAL_CAPABILITIES:
            return True

        try:
            return self.registry.can_execute(
                capability
            )
        except Exception:
            return False

    @staticmethod
    def _arguments(
        step,
        context,
    ):
        context = context or {}

        args: dict[str, Any] = {}

        metadata = (
            getattr(
                step,
                "metadata",
                {},
            )
            or {}
        )

        if isinstance(
            metadata.get("args"),
            dict,
        ):
            args.update(
                metadata["args"]
            )

        if isinstance(
            context.get("tool_args"),
            dict,
        ):
            args.update(
                context["tool_args"]
            )

        target = getattr(
            step,
            "target",
            None,
        )

        if target:
            args.setdefault(
                "path",
                target,
            )

            args.setdefault(
                "query",
                target,
            )

        return args

    def _approval_checker(
        self,
        step,
        context,
    ):
        """
        Vérifie l'approbation exacte de cette étape.

        Conditions obligatoires :

        1. approval_id présent ;
        2. run_id présent ;
        3. ApprovalRequest existante ;
        4. décision APPROVED ;
        5. même run_id ;
        6. même step_id ;
        7. même action_id ;
        8. même capability.

        Une approbation d'une autre étape ou d'un autre run
        ne peut donc pas être réutilisée.
        """

        context = context or {}

        step_metadata = (
            getattr(
                step,
                "metadata",
                {},
            )
            or {}
        )

        approval_id = (
            step_metadata.get(
                "approval_id"
            )
            or context.get(
                "approval_id"
            )
            or context.get(
                "_approval_id"
            )
        )

        if not approval_id:
            return False

        run_id = (
            context.get(
                "_execution_run_id"
            )
            or context.get(
                "run_id"
            )
            or step_metadata.get(
                "run_id"
            )
        )

        if not run_id:
            return False

        try:
            center = (
                self.runtime
                .create_approval_center()
            )

            request = center.get(
                approval_id
            )

        except Exception:
            return False

        if request is None:
            return False

        decision = getattr(
            request,
            "decision",
            None,
        )

        if decision != ApprovalDecision.APPROVED:
            return False

        request_run_id = getattr(
            request,
            "run_id",
            None,
        )

        request_metadata = (
            getattr(
                request,
                "metadata",
                None,
            )
            or {}
        )

        request_run_id = (
            request_run_id
            or request_metadata.get(
                "run_id"
            )
        )

        if request_run_id != run_id:
            return False

        request_step_id = (
            request_metadata.get(
                "step_id"
            )
        )

        if request_step_id != step.id:
            return False

        request_action_id = (
            getattr(
                request,
                "action_id",
                None,
            )
            or request_metadata.get(
                "action_id"
            )
        )

        if request_action_id != step.action_id:
            return False

        request_capability = (
            getattr(
                request,
                "capability",
                None,
            )
            or request_metadata.get(
                "capability"
            )
        )

        if request_capability != step.capability:
            return False

        return True

    def _make_tool_handler(
        self,
        capability,
    ):
        def handler(
            *,
            step,
            context=None,
        ):
            args = self._arguments(
                step,
                context,
            )

            return self.registry.execute(
                capability,
                args,
            )

        return handler

    def _make_internal_handler(
        self,
        capability,
    ):
        def handler(
            *,
            step,
            context=None,
        ):
            context = context or {}

            args = self._arguments(
                step,
                context,
            )

            if capability == "context.read":
                return {
                    "type": "context",
                    "request": context.get(
                        "request"
                    ),
                    "workspace": str(
                        self.runtime.workspace
                    ),
                    "active_file": context.get(
                        "active_file"
                    ),
                    "context": context,
                }

            if capability == "changes.propose":
                return {
                    "type": "change_proposal",
                    "status": "proposal_only",
                    "target": getattr(
                        step,
                        "target",
                        None,
                    ),
                    "request": context.get(
                        "request"
                    ),
                    "args": args,
                    "message": (
                        "Une proposition de "
                        "modification a été préparée. "
                        "Aucune modification n'est "
                        "appliquée par cette étape."
                    ),
                }

            if capability == "verification.run":
                return {
                    "type": "verification",
                    "status": "ready",
                    "target": getattr(
                        step,
                        "target",
                        None,
                    ),
                    "message": (
                        "Étape de vérification "
                        "enregistrée. La vérification "
                        "concrète peut être fournie "
                        "par le contexte d'exécution."
                    ),
                }

            if capability == "code.explain":
                return {
                    "type": "explanation",
                    "target": getattr(
                        step,
                        "target",
                        None,
                    ),
                    "request": context.get(
                        "request"
                    ),
                    "context": context,
                }

            raise KeyError(
                "Capacité interne inconnue: "
                f"{capability}"
            )

        return handler

    def register(
        self,
        capability,
        handler,
    ):
        self.executor.register(
            capability,
            handler,
        )

    def execute_step(
        self,
        step,
        context=None,
    ):
        return self.executor.execute_step(
            step,
            context or {},
        )

    def execute(
        self,
        plan,
        context=None,
    ):
        return self.executor.execute_ready(
            plan,
            context or {},
        )
