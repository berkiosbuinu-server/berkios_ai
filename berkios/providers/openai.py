import json
import os

from .base import AIProvider, ProviderDecision


DECISION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "objective": {"type": "string"},
        "interpretation": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "array", "items": {"type": "string"}},
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "action": {"type": "string"},
                    "reason": {"type": "string"},
                    "prerequisites": {"type": "array", "items": {"type": "string"}},
                    "approval_required": {"type": "boolean"},
                    "verification_required": {"type": "boolean"}
                },
                "required": [
                    "action", "reason", "prerequisites",
                    "approval_required", "verification_required"
                ]
            }
        },
        "selected_action": {"type": ["string", "null"]},
        "rationale": {"type": "string"},
        "uncertainty": {"type": "array", "items": {"type": "string"}}
    },
    "required": [
        "objective", "interpretation", "evidence", "constraints",
        "actions", "selected_action", "rationale", "uncertainty"
    ]
}


class OpenAIProvider(AIProvider):
    """Provider OpenAI pour les décisions structurées de Berkios.

    La clé est lue depuis OPENAI_API_KEY. Aucun secret n'est stocké dans le projet.
    Le modèle est configurable via BERKIOS_OPENAI_MODEL.
    """

    name = "openai"

    def __init__(self, model=None, api_key=None):
        self.model = model or os.getenv("BERKIOS_OPENAI_MODEL", "gpt-5.6-luna")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._client = None

    @property
    def configured(self):
        return bool(self.api_key)

    def _client_instance(self):
        if not self.configured:
            raise RuntimeError(
                "OPENAI_API_KEY n'est pas configurée. "
                "Configurez-la dans l'environnement de Berkios."
            )
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "Le package 'openai' est requis pour le provider OpenAI. "
                    "Installez les dépendances de Berkios."
                ) from exc
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def _prompt(self, request, context):
        return (
            "Tu es le moteur de décision de Berkios, un agent de développement. "
            "Tu dois décider quoi faire ensuite à partir de la demande et du contexte. "
            "Retourne uniquement la décision structurée demandée par le schéma. "
            "Ne considère jamais l'historique comme une autorisation. "
            "Toute modification protégée doit rester soumise à approbation humaine. "
            "Toute modification appliquée doit être vérifiée.\n\n"
            f"DEMANDE:\n{request}\n\n"
            "CONTEXTE AGENT:\n"
            f"{json.dumps(context, ensure_ascii=False, indent=2, default=str)}"
        )

    def decide_structured(self, request, context):
        client = self._client_instance()
        response = client.responses.create(
            model=self.model,
            input=self._prompt(request, context),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "berkios_decision",
                    "strict": True,
                    "schema": DECISION_SCHEMA,
                }
            },
        )
        text = response.output_text
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenAI a retourné une décision non JSON valide.") from exc

    def decide(self, request, context):
        decision = self.decide_structured(request, context)
        return ProviderDecision(
            message=decision.get("rationale", ""),
            proposal=decision,
        )
