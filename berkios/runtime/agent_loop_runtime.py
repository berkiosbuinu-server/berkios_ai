from berkios.agent.context_loop import ContextAwareAgentLoop

class AgentLoopRuntime:
    def __init__(self, agent_runtime, provider=None, lsp=None):
        self.runtime = agent_runtime
        self.loop = ContextAwareAgentLoop(
            agent_runtime,
            provider=provider,
            lsp=lsp,
        )

    def analyze(self, run_id, request, **kwargs):
        decision, context = self.loop.analyze(run_id, request, **kwargs)
        return {
            "decision": decision.to_dict(),
            "context": context.to_dict(),
        }

    def propose(self, run_id, request, **kwargs):
        decision, context = self.loop.propose(run_id, request, **kwargs)
        return {
            "decision": decision.to_dict(),
            "context": context.to_dict(),
        }

    def repair(self, run_id, request, failure, **kwargs):
        decision, context = self.loop.repair(
            run_id, request, failure, **kwargs
        )
        return {
            "decision": decision.to_dict(),
            "context": context,
        }
