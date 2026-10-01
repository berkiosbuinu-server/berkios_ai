from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any

def now():
    return datetime.now(timezone.utc).isoformat()

class TrainerStatus(str, Enum):
    CREATED="created"
    RUNNING="running"
    CHECKPOINTED="checkpointed"
    COMPLETED="completed"
    FAILED="failed"
    CANCELLED="cancelled"

@dataclass
class TrainerConfig:
    epochs: int = 1
    batch_size: int = 4
    learning_rate: float = 2e-5
    checkpoint_every_steps: int = 10
    max_steps: int | None = None
    seed: int = 42
    output_dir: str = ".berkios/models"

@dataclass
class TrainerCheckpoint:
    run_id: str
    step: int
    epoch: int
    artifact: str
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=now)

@dataclass
class TrainerResult:
    run_id: str
    status: TrainerStatus
    steps: int
    epochs_completed: int
    artifact: str | None = None
    checkpoint: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    reason: str | None = None
