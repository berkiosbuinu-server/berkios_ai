from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Any
import uuid

@dataclass
class LearningConsent:
    enabled: bool=False
    scope: list[str]=field(default_factory=list)
    user_id: str|None=None
    granted_at: str|None=None
    revoked_at: str|None=None
    def grant(self,scope=None):
        self.enabled=True; self.scope=list(scope or [])
        self.granted_at=datetime.now(timezone.utc).isoformat(); self.revoked_at=None
    def revoke(self):
        self.enabled=False; self.revoked_at=datetime.now(timezone.utc).isoformat()

@dataclass
class LearningExample:
    example_id: str=field(default_factory=lambda:str(uuid.uuid4()))
    source: str="ibook"
    provider: str|None=None
    model: str|None=None
    task: str=""
    input_data: dict[str,Any]=field(default_factory=dict)
    output_data: dict[str,Any]=field(default_factory=dict)
    feedback: str|None=None
    score: float|None=None
    project_hash: str|None=None
    consent_required: bool=True
    created_at: str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
    def to_dict(self): return self.__dict__.copy()
