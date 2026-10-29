from __future__ import annotations

from .run import ExecutionRun, RunState


class ExecutionController:
    """
    Contrôleur canonique d'exécution.

    Il orchestre :
    - l'état du run ;
    - les étapes ;
    - les résultats ;
    - la persistance ;
    - la reprise ;
    - les demandes d'approbation.
    """

    def __init__(self, executor, persistence=None, runtime=None):
        self.executor = executor
        self.persistence = persistence
        self.runtime = runtime
        self.runs = {}

        self._restore()

    # ---------------------------------------------------------
    # Restore
    # ---------------------------------------------------------

    def _restore(self):
        if self.persistence is None:
            return

        try:
            rows = self.persistence.repository.list_runs()
        except Exception:
            return

        for row in rows:
            payload = row.get("payload") or {}

            run_data = (
                payload.get("run")
                if isinstance(payload, dict)
                else None
            )

            if not isinstance(run_data, dict):
                continue

            try:
                run = ExecutionRun(
                    run_id=run_data.get(
                        "run_id",
                        row["id"],
                    ),
                    request=run_data.get(
                        "request",
                        "",
                    ),
                    state=RunState(
                        run_data.get(
                            "state",
                            row.get(
                                "state",
                                "created",
                            ),
                        )
                    ),
                    results=run_data.get(
                        "results",
                        [],
                    ),
                    events=run_data.get(
                        "events",
                        [],
                    ),
                    created_at=run_data.get(
                        "created_at"
                    ) or "",
                    plan=run_data.get("plan"),
                    context=run_data.get(
                        "context",
                        {},
                    ),
                )

                self.runs[run.run_id] = run

            except Exception:
                continue

    # ---------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------

    def _persist(self, run):
        if self.persistence is None:
            return

        try:
            payload = {
                "run": run.to_dict(),
            }

            record = getattr(
                self.persistence,
                "record_run",
                None,
            )

            workspace = (
                str(
                    getattr(
                        self.persistence,
                        "workspace",
                        "",
                    )
                )
                or None
            )

            if callable(record):
                record(
                    run.run_id,
                    run.state.value,
                    payload,
                    workspace,
                )
                return

            repository = getattr(
                self.persistence,
                "repository",
                None,
            )

            if repository is not None:
                repository.upsert_run(
                    run.run_id,
                    run.state.value,
                    payload,
                    workspace,
                )

        except Exception:
            pass

    def _emit(self, run, event, **data):
        item = run.emit(
            event,
            **data,
        )

        if self.persistence is not None:
            try:
                self.persistence.record_event(
                    event,
                    item,
                    run.run_id,
                )
            except Exception:
                pass

        self._persist(run)

        return item

    # ---------------------------------------------------------
    # Approval
    # ---------------------------------------------------------

    def _existing_approval_for_step(
        self,
        run,
        step,
    ):
        """
        Recherche une approbation déjà attachée à cette étape.

        Cette vérification évite de créer plusieurs ApprovalRequest
        pour la même étape si l'exécution est relancée.
        """

        for result in run.results:
            if result.get("step_id") != step.id:
                continue

            metadata = result.get("metadata") or {}

            approval_id = metadata.get("approval_id")

            if not approval_id:
                continue

            if self.runtime is None:
                return approval_id

            try:
                request = (
                    self.runtime
                    .create_approval_center()
                    .get(approval_id)
                )

                if request is not None:
                    return request

            except Exception:
                return approval_id

        return None

    def _request_approval(
        self,
        run,
        step,
        result_dict,
    ):
        """
        Crée et persiste automatiquement la demande d'approbation
        lorsque l'exécution atteint une étape protégée.

        Le contrôleur reste le seul endroit qui connaît simultanément :
        - le run ;
        - le step ;
        - l'action ;
        - le résultat d'exécution.
        """

        existing = self._existing_approval_for_step(
            run,
            step,
        )

        if existing is not None:
            if hasattr(existing, "approval_id"):
                approval_id = existing.approval_id
            else:
                approval_id = existing

            metadata = result_dict.setdefault(
                "metadata",
                {},
            )

            metadata.update(
                {
                    "approval_id": approval_id,
                    "run_id": run.run_id,
                    "step_id": step.id,
                    "action_id": step.action_id,
                    "capability": step.capability,
                }
            )

            # L'approbation est également attachée à l'étape.
            # Elle reste ainsi liée à cette exécution précise.
            step.metadata["approval_id"] = approval_id
            step.metadata["run_id"] = run.run_id
            step.metadata["step_id"] = step.id
            step.metadata["action_id"] = step.action_id
            step.metadata["capability"] = step.capability

            return existing

        if self.runtime is None:
            raise RuntimeError(
                "Impossible de créer une approbation : "
                "runtime indisponible."
            )

        center = self.runtime.create_approval_center()

        metadata = dict(
            step.metadata or {}
        )

        metadata.setdefault(
            "step_id",
            step.id,
        )

        metadata.setdefault(
            "action_id",
            step.action_id,
        )

        metadata.setdefault(
            "run_id",
            run.run_id,
        )

        metadata.setdefault(
            "capability",
            step.capability,
        )

        targets = []

        if step.target:
            targets.append(
                str(step.target)
            )

        changes = []

        if step.metadata:
            raw_changes = step.metadata.get(
                "changes"
            )

            if isinstance(raw_changes, list):
                changes = raw_changes

        request = center.request(
            run_id=run.run_id,
            action_id=step.action_id,
            capability=step.capability,
            title=(
                "Approbation requise : "
                f"{step.action_id}"
            ),
            description=(
                step.reason
                or "Cette étape nécessite "
                   "une approbation explicite."
            ),
            risk=(
                step.metadata.get(
                    "risk",
                    "medium",
                )
                if step.metadata
                else "medium"
            ),
            targets=targets,
            changes=changes,
            reason=(
                step.reason
                or (
                    "L'étape "
                    f"{step.id} demande une approbation."
                )
            ),
            metadata=metadata,
        )

        result_metadata = result_dict.setdefault(
            "metadata",
            {},
        )

        result_metadata.update(
            {
                "approval_id": request.approval_id,
                "run_id": run.run_id,
                "step_id": step.id,
                "action_id": step.action_id,
                "capability": step.capability,
            }
        )

        # L'approbation doit être attachée à l'étape elle-même.
        # Cela permet à la reprise de retrouver l'autorisation
        # exacte sans autoriser globalement la capability.
        step.metadata["approval_id"] = request.approval_id
        step.metadata["run_id"] = run.run_id
        step.metadata["step_id"] = step.id
        step.metadata["action_id"] = step.action_id
        step.metadata["capability"] = step.capability

        self._emit(
            run,
            "approval.requested",
            approval_id=request.approval_id,
            step_id=step.id,
            action_id=step.action_id,
            capability=step.capability,
        )

        return request

    # ---------------------------------------------------------
    # Run
    # ---------------------------------------------------------

    def create(self, request):
        run = ExecutionRun(
            request=request,
        )

        self.runs[run.run_id] = run

        self._emit(
            run,
            "execution.created",
        )

        return run

    def get(self, run_id):
        return self.runs.get(run_id)

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def cancel(self, run_id):
        run = self.get(run_id)

        if run is None:
            raise KeyError(run_id)

        if run.state in {
            RunState.COMPLETED,
            RunState.FAILED,
            RunState.CANCELLED,
        }:
            return run

        run.state = RunState.CANCELLED

        self._emit(
            run,
            "execution.cancelled",
        )

        return run

    def pause(self, run_id):
        run = self.get(run_id)

        if run is None:
            raise KeyError(run_id)

        if run.state == RunState.RUNNING:
            run.state = RunState.PAUSED

            self._emit(
                run,
                "execution.paused",
            )

        return run

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def _execute_from_current_state(
        self,
        run,
        plan,
        context,
    ):
        # -----------------------------------------------------
        # Contexte canonique d'exécution
        # -----------------------------------------------------
        #
        # Le contexte peut provenir :
        # - d'une nouvelle exécution ;
        # - d'une reprise après approbation.
        #
        # On le copie afin de ne jamais modifier directement
        # le dictionnaire fourni par l'appelant.
        execution_context = dict(context or {})

        # Le run_id est toujours déterminé par le run chargé
        # par le contrôleur. Il ne doit jamais être fourni
        # arbitrairement par le contexte utilisateur.
        execution_context["_execution_run_id"] = run.run_id

        run.plan = plan.to_dict()
        run.context = execution_context

        for step in plan.steps:
            completed_ids = {
                item.get("step_id")
                for item in run.results
                if item.get("success")
            }

            if step.id in completed_ids:
                continue

            if any(
                dependency not in completed_ids
                for dependency in step.depends_on
            ):
                continue

            if run.state in {
                RunState.CANCELLED,
                RunState.PAUSED,
            }:
                break

            self._emit(
                run,
                "execution.step.started",
                step_id=step.id,
            )

            # IMPORTANT :
            # utiliser exactement le contexte canonique,
            # notamment _execution_run_id et approval_id.
            result = self.executor.execute_step(
                step,
                execution_context,
            )

            result_dict = result.to_dict()

            existing = next(
                (
                    item
                    for item in run.results
                    if item.get("step_id") == step.id
                ),
                None,
            )

            if existing is None:
                run.results.append(result_dict)
            else:
                existing.clear()
                existing.update(result_dict)

            self._emit(
                run,
                (
                    "execution.step.completed"
                    if result.success
                    else "execution.step.failed"
                ),
                step_id=step.id,
                result=result_dict,
            )

            # -------------------------------------------------
            # APPROBATION
            # -------------------------------------------------

            if result.state.value == "waiting_approval":
                try:
                    self._request_approval(
                        run,
                        step,
                        result_dict,
                    )

                except Exception as exc:
                    run.state = RunState.FAILED

                    self._emit(
                        run,
                        "approval.request_failed",
                        step_id=step.id,
                        action_id=step.action_id,
                        error=str(exc),
                    )

                    self._persist(run)

                    return run

                # _request_approval() a pu enrichir step.metadata
                # avec approval_id. On reconstruit donc le plan
                # avant sa persistance.
                run.plan = plan.to_dict()

                # Le contexte canonique doit également être
                # conservé avec le run pour la reprise durable.
                run.context = execution_context

                run.state = RunState.WAITING_APPROVAL

                self._emit(
                    run,
                    "execution.waiting_approval",
                    step_id=step.id,
                    action_id=step.action_id,
                    approval_id=(
                        result_dict
                        .get("metadata", {})
                        .get("approval_id")
                    ),
                )

                self._persist(run)

                return run

            if not result.success:
                run.state = RunState.FAILED

                self._emit(
                    run,
                    "execution.failed",
                    step_id=step.id,
                )

                return run

        completed_ids = {
            item.get("step_id")
            for item in run.results
            if item.get("success")
        }

        pending = [
            step
            for step in plan.steps
            if step.id not in completed_ids
        ]

        if not pending:
            run.state = RunState.COMPLETED

            self._emit(
                run,
                "execution.completed",
            )

        else:
            executable = [
                step
                for step in pending
                if all(
                    dependency in completed_ids
                    for dependency in step.depends_on
                )
            ]

            if executable:
                run.state = RunState.RUNNING

            else:
                run.state = RunState.FAILED

                self._emit(
                    run,
                    "execution.blocked",
                )

        self._persist(run)

        return run

    # ---------------------------------------------------------
    # Execute
    # ---------------------------------------------------------

    def execute(
        self,
        run_id,
        plan,
        context=None,
    ):
        run = self.get(run_id)

        if run is None:
            raise KeyError(run_id)

        if run.state == RunState.CANCELLED:
            return run

        run.plan = plan.to_dict()

        execution_context = dict(
            context or {}
        )

        execution_context["_execution_run_id"] = (
            run.run_id
        )

        run.context = execution_context
        run.state = RunState.RUNNING

        self._emit(
            run,
            "execution.started",
        )

        return self._execute_from_current_state(
            run,
            plan,
            context or {},
        )

    # ---------------------------------------------------------
    # Resume
    # ---------------------------------------------------------

    def resume(
        self,
        run_id,
        plan,
        context=None,
    ):
        run = self.get(run_id)

        if run is None:
            raise KeyError(run_id)

        if run.state in {
            RunState.CANCELLED,
            RunState.COMPLETED,
            RunState.FAILED,
        }:
            return run

        run.plan = plan.to_dict()

        execution_context = dict(
            context
            or run.context
            or {}
        )

        # Le run_id canonique vient toujours du run chargé
        # par le contrôleur.
        execution_context["_execution_run_id"] = (
            run.run_id
        )

        run.context = execution_context
        run.state = RunState.RUNNING

        self._emit(
            run,
            "execution.resumed",
        )

        return self._execute_from_current_state(
            run,
            plan,
            run.context,
        )
