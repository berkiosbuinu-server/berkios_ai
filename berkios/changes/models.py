from dataclasses import dataclass, field
from enum import Enum
import uuid

class ChangeStatus(str, Enum):
    PENDING="pending"; ACCEPTED="accepted"; REJECTED="rejected"; APPLIED="applied"

@dataclass
class FileEdit:
    path: str
    old_text: str
    new_text: str

@dataclass
class ChangeProposal:
    edits: list[FileEdit]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: ChangeStatus = ChangeStatus.PENDING

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status.value,
            "edits": [e.__dict__ for e in self.edits],
        }
