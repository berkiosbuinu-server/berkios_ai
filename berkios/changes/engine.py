from pathlib import Path
from .models import ChangeProposal, ChangeStatus

class ChangeEngine:
    def __init__(self, workspace):
        self.workspace = Path(workspace).resolve()

    def _path(self, value):
        p = (self.workspace / value).resolve()
        if p != self.workspace and self.workspace not in p.parents:
            raise ValueError("Path outside workspace")
        return p

    def validate(self, proposal):
        for edit in proposal.edits:
            p = self._path(edit.path)
            if not p.exists():
                raise FileNotFoundError(edit.path)
            text = p.read_text(encoding="utf-8")
            if edit.old_text not in text:
                raise ValueError(f"Old text not found: {edit.path}")
        return True

    def preview(self, proposal):
        self.validate(proposal)
        return [{"path": e.path, "old": e.old_text, "new": e.new_text} for e in proposal.edits]

    def apply(self, proposal):
        self.validate(proposal)
        for edit in proposal.edits:
            p = self._path(edit.path)
            text = p.read_text(encoding="utf-8")
            p.write_text(text.replace(edit.old_text, edit.new_text, 1), encoding="utf-8")
        proposal.status = ChangeStatus.APPLIED
        return proposal
