from dataclasses import dataclass

@dataclass
class ProviderDecision:
    message: str = ""
    tool_call: tuple | None = None
    proposal: object | None = None

class AIProvider:
    name = "base"
    def decide(self, request, context) -> ProviderDecision:
        raise NotImplementedError
