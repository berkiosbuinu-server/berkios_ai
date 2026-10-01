from berkios.agent.run_context import AgentRunContext

class IntelligenceAgentLoop:
    """Small integration facade for existing AgentLoop implementations."""

    def __init__(self, workspace, runtime=None, run_memory=None, loop=None):
        self.context = AgentRunContext(workspace, runtime, run_memory)
        self.loop = loop

    def start(self, request: str, **kwargs):
        prepared = self.context.prepare(request, **kwargs)
        self.context.record_transition(
            "analyzing",
            {"intelligence_ready": True}
        )
        return prepared

    def transition(self, state: str, detail=None):
        self.context.record_transition(state, detail)

    def decision(self, decision):
        self.context.record_decision(decision)

    def verification(self, result):
        self.context.record_verification(result)
