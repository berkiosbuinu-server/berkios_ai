from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()

class ManagerState(str, Enum):
    QUEUED="queued"; COLLECTING="collecting"; DATASET_READY="dataset_ready"
    TRAINING="training"; VALIDATING="validating"; READY_TO_PROMOTE="ready_to_promote"
    PROMOTED="promoted"; REJECTED="rejected"; FAILED="failed"; CANCELLED="cancelled"

@dataclass
class TrainingVersion:
    version: str
    artifact: str|None
    score: float
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=now)

@dataclass
class ManagedTrainingRun:
    run_id: str
    dataset_id: str
    dataset_version: str
    base_version: str|None
    state: ManagerState=ManagerState.QUEUED
    progress: float=0.0
    metrics: dict = field(default_factory=dict)
    current_version: str|None=None
    error: str|None=None
    created_at: str=field(default_factory=now)
    updated_at: str=field(default_factory=now)
