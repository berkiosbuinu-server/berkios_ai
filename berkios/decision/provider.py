from .models import Decision, DecisionAction


class ProviderDecisionIntegration:
    """Transforme une sortie structurée de provider en Decision canonique."""

    def normalize(self, request, payload):
        if not isinstance(payload, dict):
            raise ValueError("La décision provider doit être un objet JSON.")

        actions = []
        for item in payload.get("actions", []):
            if not isinstance(item, dict) or not item.get("action"):
                continue
            actions.append(DecisionAction(
                action=str(item["action"]),
                reason=str(item.get("reason", "")),
                prerequisites=[str(x) for x in item.get("prerequisites", [])],
                approval_required=bool(item.get("approval_required", True)),
                verification_required=bool(item.get("verification_required", True)),
            ))

        selected = payload.get("selected_action")
        if selected is not None:
            selected = str(selected)

        return Decision(
            request=request,
            objective=str(payload.get("objective", request)),
            interpretation=str(payload.get("interpretation", "")),
            evidence=[str(x) for x in payload.get("evidence", [])],
            constraints=[str(x) for x in payload.get("constraints", [])],
            actions=actions,
            selected_action=selected,
            rationale=str(payload.get("rationale", "")),
            uncertainty=[str(x) for x in payload.get("uncertainty", [])],
        )

    def decide(self, provider_engine, request, context):
        provider = provider_engine.current()
        if not hasattr(provider, "decide_structured"):
            raise RuntimeError(
                f"Le provider '{provider.name}' ne fournit pas de décision structurée."
            )
        payload = provider.decide_structured(request, context)
        return self.normalize(request, payload)
