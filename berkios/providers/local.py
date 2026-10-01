from .base import AIProvider, ProviderDecision

class LocalProvider(AIProvider):
    name = "local"
    def decide(self, request, context):
        return ProviderDecision(
            message=f"Analyse locale reçue pour: {request}",
        )
