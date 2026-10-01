from pathlib import Path
from .models import ProjectContextSnapshot

class ProjectContextFusion:
    """Fusionne les différentes intelligences Berkios en un contexte unique."""

    def __init__(self, workspace, project_understanding=None, explainer=None,
                 explorer=None, graph=None, change_planner=None,
                 verifier=None, repair=None):
        self.workspace=Path(workspace).resolve()
        self.project_understanding=project_understanding
        self.explainer=explainer
        self.explorer=explorer
        self.graph=graph
        self.change_planner=change_planner
        self.verifier=verifier
        self.repair=repair

    def build(self, request="", target=None, active_file=None, selection=None,
              diagnostics=None, memory=None):
        target=target or active_file
        snapshot=ProjectContextSnapshot(
            workspace=str(self.workspace),
            request=request,
            active_file=active_file,
            selection=selection,
            diagnostics=list(diagnostics or []),
            relevant_memory=list(memory or []),
        )

        if self.project_understanding:
            try: snapshot.project_understanding=self.project_understanding.analyze().to_dict()
            except Exception as e: snapshot.project_understanding={"error":str(e)}

        if target and self.explainer:
            try: snapshot.code_explanation=self.explainer.explain_file(target).to_dict()
            except Exception as e: snapshot.code_explanation={"error":str(e)}

        if target and self.explorer:
            try: snapshot.code_exploration=self.explorer.explore_file(target).to_dict()
            except Exception as e: snapshot.code_exploration={"error":str(e)}

        if target and self.graph:
            try: snapshot.graph_impact=self.graph.impact(target).to_dict()
            except Exception as e: snapshot.graph_impact={"error":str(e)}

        if target and self.change_planner:
            try: snapshot.change_plan=self.change_planner.plan(target,request).to_dict()
            except Exception as e: snapshot.change_plan={"error":str(e)}

        snapshot.summary=self._summary(snapshot)
        return snapshot

    def _summary(self,s):
        parts=[]
        pu=s.project_understanding
        if pu.get("summary"): parts.append(pu["summary"])
        if s.code_explanation.get("purpose"): parts.append("Rôle : "+s.code_explanation["purpose"])
        if s.graph_impact.get("explanation"): parts.append(s.graph_impact["explanation"])
        if s.change_plan.get("affected_files"):
            parts.append(f"{len(s.change_plan['affected_files'])} fichier(s) dans le périmètre.")
        if s.diagnostics:
            parts.append(f"{len(s.diagnostics)} diagnostic(s) actif(s).")
        return " ".join(parts)
