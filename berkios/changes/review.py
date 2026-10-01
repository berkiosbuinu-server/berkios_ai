from .models import ChangeProposal, ChangeStatus

class ChangeReview:
    def __init__(self):
        self.proposals = {}

    def add(self, proposal):
        self.proposals[proposal.id] = proposal
        return proposal

    def get(self, proposal_id):
        return self.proposals[proposal_id]

    def accept(self, proposal_id):
        proposal = self.get(proposal_id)
        proposal.status = ChangeStatus.ACCEPTED
        return proposal

    def reject(self, proposal_id):
        proposal = self.get(proposal_id)
        proposal.status = ChangeStatus.REJECTED
        return proposal

    def list(self):
        return [p.to_dict() for p in self.proposals.values()]
