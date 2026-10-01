from pathlib import Path
import uuid

from .models import EngineeringRun, EngineeringState

class EngineeringLoop:
    """Orchestre les briques d'intelligence du cycle logiciel Berkios."""

    def __init__(self, workspace, explainer=None, explorer=None,
                 change_planner=None, verifier=None, repair=None):
        self.workspace=Path(workspace).resolve()
        self.explainer=explainer
        self.explorer=explorer
        self.change_planner=change_planner
        self.verifier=verifier
        self.repair=repair

    def start(self, target, request):
        run=EngineeringRun(
            run_id=uuid.uuid4().hex,
            target=target,
            request=request,
        )
        self._state(run,"analyzing","Analyse du code et du contexte.")
        if self.explainer:
            try:
                run.explanation=self.explainer.explain_file(target).to_dict()
            except Exception as e:
                run.explanation={"error":str(e)}

        if self.explorer:
            try:
                run.impact=self.explorer.explore_file(target).to_dict()
            except Exception as e:
                run.impact={"error":str(e)}

        self._state(run,"planning","Préparation du changement.")
        if self.change_planner:
            try:
                plan=self.change_planner.plan(target,request)
                run.impact["change_plan"]=plan.to_dict()
                run.states[-1].approval_required=plan.approval_required
            except Exception as e:
                run.impact["planning_error"]=str(e)

        self._state(run,"waiting_approval","Une modification peut nécessiter une approbation.",approval=True)
        return run

    def record_verification(self, run, passed, message="", error_kind="unknown"):
        self._state(run,"verifying",message)
        if passed:
            run.result="completed"
            self._state(run,"completed","Vérification réussie.")
            return run

        self._state(run,"repairing","Échec détecté : préparation d'une réparation.")
        if self.repair:
            try:
                ctx=self.repair.prepare(
                    change_target=run.target,
                    error_message=message,
                    error_kind=error_kind,
                    affected_files=[run.target],
                )
                run.repair_context=ctx.to_dict()
            except Exception as e:
                run.repair_context={"error":str(e)}

        run.result="repair_required"
        return run

    def approve(self, run):
        self._state(run,"approved","Approbation reçue.")
        return run

    def _state(self,run,state,message,approval=False):
        run.states.append(EngineeringState(
            state=state,
            message=message,
            step=len(run.states)+1,
            approval_required=approval,
        ))
