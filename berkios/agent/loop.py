from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

class LoopState(str, Enum):
    IDLE="idle"; ANALYZING="analyzing"; PROPOSING="proposing"
    WAITING_APPROVAL="waiting_approval"; APPLYING="applying"
    VERIFYING="verifying"; REPAIRING="repairing"; COMPLETED="completed"; FAILED="failed"

@dataclass
class LoopEvent:
    run_id: str
    state: LoopState
    message: str
    data: dict = field(default_factory=dict)
    at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AgentLoop:
    def __init__(self, workspace, request, run_id=None, context=None,
                 project_memory=None, session_memory=None, providers=None,
                 tools=None, changes=None, verification=None, review=None, corrections=None):
        self.workspace = workspace
        self.request = request
        self.run_id = run_id or uuid.uuid4().hex
        self.context = context
        self.project_memory = project_memory
        self.session_memory = session_memory
        self.providers = providers
        self.tools = tools
        self.changes = changes
        self.verification = verification
        self.review = review
        self.corrections = corrections
        self.state = LoopState.IDLE
        self.events = []
        self.memory = None
        self.proposal = None
        self.approval_required = False
        self.result = None
        self.recalled_corrections = []

    def emit(self, state, message, data=None):
        self.state = state
        event = LoopEvent(self.run_id, state, message, data or {})
        self.events.append(event)
        if self.memory:
            self.memory.add("transition", message)
        return event

    def start(self):
        from ..memory.run import RunMemory
        self.memory = RunMemory(self.workspace, self.run_id)
        self.memory.add("request", self.request)
        self.emit(LoopState.ANALYZING, "Recherche des corrections historiques similaires.")
        self.recalled_corrections = []
        self.emit(LoopState.ANALYZING, "Analyse de la demande et du contexte.")
        context = self.context.compose(self.request) if self.context else {"request": self.request}
        provider = self.providers.current()
        self.emit(LoopState.PROPOSING, "Le provider prépare une décision.")
        decision = provider.decide(self.request, context)
        self.memory.add("decision", decision.message)

        # Une proposition peut être injectée par un provider avancé.
        proposal = getattr(decision, "proposal", None)
        if proposal is not None:
            self.proposal = self.review.add(proposal) if self.review else proposal
            self.approval_required = True
            self.emit(
                LoopState.WAITING_APPROVAL,
                "Une modification attend l'approbation de l'utilisateur.",
                {"proposal": self.proposal.to_dict()}
            )
            return self.snapshot()

        self.result = {"message": decision.message}
        self.emit(LoopState.COMPLETED, decision.message or "Run terminé.")
        return self.snapshot()

    def approve(self):
        if self.proposal is None:
            raise RuntimeError("No pending proposal")
        if self.review:
            self.review.accept(self.proposal.id)
        self.approval_required = False
        self.emit(LoopState.APPLYING, "Application de la proposition.", {"proposal_id": self.proposal.id})
        self.changes.apply(self.proposal)
        self.memory.add("proposal", self.proposal.to_dict())
        return self.verify()

    def deny(self):
        if self.proposal is None:
            raise RuntimeError("No pending proposal")
        if self.review:
            self.review.reject(self.proposal.id)
        self.approval_required = False
        self.emit(LoopState.FAILED, "Proposition refusée par l'utilisateur.",
                  {"proposal_id": self.proposal.id})
        return self.snapshot()

    def verify(self):
        self.emit(LoopState.VERIFYING, "Vérification des changements.")
        paths = [e.path for e in self.proposal.edits] if self.proposal else []
        result = self.verification.files(paths)
        self.memory.add("verification", result)
        if result["ok"]:
            self.emit(LoopState.COMPLETED, "Modifications appliquées et vérifiées.")
            self.result = result
            return self.snapshot()

        self.emit(LoopState.REPAIRING, "La vérification a échoué; une réparation peut être proposée.",
                  {"verification": result})
        self.emit(LoopState.FAILED, "Run arrêté après échec de vérification.")
        self.result = result
        return self.snapshot()

    def run(self, auto_apply=False):
        result = self.start()
        if auto_apply and self.proposal is not None and self.state == LoopState.WAITING_APPROVAL:
            return self.approve()
        return result

    def snapshot(self):
        return {
            "run_id": self.run_id,
            "state": self.state.value,
            "request": self.request,
            "approval_required": self.approval_required,
            "proposal": self.proposal.to_dict() if self.proposal else None,
            "result": self.result,
            "recalled_corrections": self.recalled_corrections,
            "events": [
                {"run_id": e.run_id, "state": e.state.value, "message": e.message,
                 "data": e.data, "at": e.at}
                for e in self.events
            ],
            "memory": self.memory.list() if self.memory else [],
        }
