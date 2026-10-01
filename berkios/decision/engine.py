from .models import Decision, DecisionAction

class DecisionEngine:
    def decide(self, request, context=None, target=None):
        context=context or {}
        evidence=[]
        for key in ("summary","code_explanation","code_exploration","graph_impact","change_plan"):
            v=context.get(key)
            if isinstance(v,dict):
                if v.get("summary"): evidence.append(str(v["summary"]))
                if v.get("explanation"): evidence.append(str(v["explanation"]))
                if v.get("risk_level"): evidence.append("Impact: "+str(v["risk_level"]))
            elif v: evidence.append(str(v))
        if context.get("diagnostics"):
            evidence.append(f"{len(context['diagnostics'])} diagnostic(s) actif(s).")

        constraints=[
            "Respecter les permissions du runtime.",
            "Ne pas transformer l'historique en autorisation.",
            "Vérifier toute modification appliquée."
        ]
        low=request.lower()
        actions=[]
        if any(x in low for x in ("explique","explain","comprendre")):
            actions=[DecisionAction("explain","La demande porte sur la compréhension.",[],False,False)]
            interpretation="Compréhension et explication."
        elif any(x in low for x in ("corrige","fix","répare","repair")):
            actions=[
                DecisionAction("analyze_and_propose_repair","Analyser puis proposer la réparation.",["diagnostic","impact analysis"]),
                DecisionAction("inspect_only","Inspecter sans modifier.",[],False,False)
            ]
            interpretation="Diagnostic et réparation."
        elif any(x in low for x in ("modifie","ajoute","change","refactor","implement")):
            actions=[
                DecisionAction("analyze_and_propose_change","Analyser puis proposer la modification.",["context","impact analysis","change proposal"]),
                DecisionAction("explain_impact_first","Présenter d'abord l'impact.",[],False,False)
            ]
            interpretation="Modification ou évolution du projet."
        else:
            actions=[DecisionAction("analyze","Commencer par analyser la demande.",[],False,False)]
            interpretation="Analyse de la demande."

        uncertainty=[]
        if not target: uncertainty.append("Aucune cible explicite.")
        if not evidence: uncertainty.append("Contexte limité.")
        return Decision(
            request=request, objective=request, interpretation=interpretation,
            evidence=evidence, constraints=constraints, actions=actions,
            selected_action=actions[0].action if actions else None,
            rationale=f"Décision basée sur {len(evidence)} élément(s) de contexte.",
            uncertainty=uncertainty)
