from berkios.intelligence.repair_context import ErrorGuidedRepairContext
from berkios.providers.agent_decision import ProviderDecisionAdapter
from berkios.runtime.agent_runtime import RuntimeState

class ErrorGuidedRepairLoop:
    def __init__(self, runtime, provider=None):
        self.runtime = runtime
        self.context = ErrorGuidedRepairContext(
            runtime.workspace,
            getattr(runtime, "runtime", None),
        )
        self.provider = ProviderDecisionAdapter(provider)

    def prepare(self, run_id: str, request: str, failure: dict,
                affected_files=None, affected_symbols=None):
        context = self.context.build(
            request,
            failure,
            affected_files=affected_files,
            affected_symbols=affected_symbols,
        )
        self.runtime.transition(
            run_id,
            RuntimeState.REPAIRING,
            error_guided=True,
        )
        return context

    def decide(self, run_id: str, request: str, failure: dict,
               affected_files=None, affected_symbols=None):
        context = self.prepare(
            run_id,
            request,
            failure,
            affected_files,
            affected_symbols,
        )
        decision = self.provider.decide(request, context.to_dict())
        self.runtime.record_decision(run_id, {
            "phase": "error_guided_repair",
            "decision": decision.to_dict(),
        })
        return decision, context
