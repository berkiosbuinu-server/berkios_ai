from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any

def now():
    return datetime.now(timezone.utc).isoformat()

class TrainingStatus(str, Enum):
    CREATED="created"
    EVALUATING="evaluating"
    PREPARING="preparing"
    TRAINING="training"
    VALIDATING="validating"
    PROMOTED="promoted"
    REJECTED="rejected"
    FAILED="failed"

@dataclass
class AutoTrainingConfig:
    min_quality_score: float = 0.80
    min_validation_score: float = 0.80
    max_quality_drop: float = 0.03
    require_consent: bool = True
    require_human_approval: bool = True
    epochs: int = 1
    batch_size: int = 4
    learning_rate: float = 2e-5
    backend: str = "adapter"
    auto_promote: bool = False

@dataclass
class AutoTrainingRun:
    run_id: str
    dataset_id: str
    dataset_version: str
    base_model: str
    status: TrainingStatus = TrainingStatus.CREATED
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    artifact: str | None = None
    reason: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)
