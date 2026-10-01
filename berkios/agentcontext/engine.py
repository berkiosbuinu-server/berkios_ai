from .models import AgentContext, ContextSection

class AgentContextEngine:
    """Transforme un snapshot projet en contexte priorisé pour l'agent."""

    def build(self, request, target=None, snapshot=None, active_file=None,
              selection=None, diagnostics=None):
        snapshot=snapshot or {}
        sections=[]

        def add(name,content,priority,reason):
            if content:
                sections.append(ContextSection(name,content,priority,reason))

        add("request",request,1.0,"Demande explicite de l'utilisateur.")
        add("active_file",active_file,0.95,"Fichier actuellement ouvert dans iBook.")
        add("selection",selection,1.0,"Code directement sélectionné par l'utilisateur.")
        add("diagnostics",diagnostics,0.98,"Erreurs et diagnostics actifs.")
        add("code_explanation",snapshot.get("code_explanation"),0.9,
            "Explique le rôle du code ciblé.")
        add("code_exploration",snapshot.get("code_exploration"),0.88,
            "Décrit les connexions du code.")
        add("graph_impact",snapshot.get("graph_impact"),0.92,
            "Détermine l'impact potentiel.")
        add("change_plan",snapshot.get("change_plan"),0.94,
            "Décrit le périmètre du changement.")
        add("project_understanding",snapshot.get("project_understanding"),0.82,
            "Fournit la vision globale du projet.")
        add("relevant_memory",snapshot.get("relevant_memory"),0.72,
            "Réutilise les connaissances historiques pertinentes.")
        add("verification",snapshot.get("verification"),0.9,
            "Résultats de vérification récents.")
        add("repair_context",snapshot.get("repair_context"),0.96,
            "Contexte d'une réparation en cours.")

        sections.sort(key=lambda s:s.priority,reverse=True)

        constraints=[
            "Respecter les permissions du runtime.",
            "Ne pas considérer l'historique comme une autorisation.",
            "Présenter une proposition avant toute modification protégée.",
            "Vérifier les changements après application.",
        ]

        instructions=[
            "Comprendre le contexte avant de décider.",
            "Privilégier les changements minimaux et ciblés.",
            "Utiliser les connexions et l'impact pour anticiper les effets.",
            "Expliquer la raison d'une décision lorsque c'est pertinent.",
        ]

        summary=self._summary(sections,target)
        return AgentContext(
            request=request,
            target=target,
            sections=sections,
            instructions=instructions,
            constraints=constraints,
            summary=summary,
        )

    def _summary(self,sections,target):
        names=[s.name for s in sections]
        target_text=f" sur {target}" if target else ""
        return "Contexte agent construit"+target_text+": "+", ".join(names)
