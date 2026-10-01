from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()

class LoopState(str, Enum):
    IDLE="idle"; COLLECTING="collecting"; DATASET="dataset"; TRAINING="training"
    EVALUATING="evaluating"; PROMOTING="promoting"; COMPLETED="completed"
    REJECTED="rejected"; FAILED="failed"; CANCELLED="cancelled"

@dataclass
class LoopConfig:
    min_new_examples:int=10
    min_validation_score:float=.80
    max_regression:float=.03
    auto_promote:bool=False

@dataclass
class ContinuousRun:
    run_id:str
    state:LoopState=LoopState.IDLE
    progress:float=0.0
    metrics:dict=field(default_factory=dict)
    version:str|None=None
    reason:str|None=None
    created_at:str=field(default_factory=now)
    updated_at:str=field(default_factory=now)
