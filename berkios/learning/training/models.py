from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExampleStatus(str, Enum):
    RAW = "raw"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class TrainingStage(str, Enum):
    COLLECT = "collect"
    REVIEW = "review"
    CURATE = "curate"
    EVALUATE = "evaluate"
    EXPORT = "export"
    TRAIN = "train"
    PROMOTE = "promote"


@dataclass
class CuratedExample:
    example_id: str
    task: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    provider: str | None = None
    model: str | None = None
    feedback: str | None = None
    score: float | None = None
    status: ExampleStatus = ExampleStatus.RAW
    redactions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self):
        d = self.__dict__.copy()
        d["status"] = self.status.value
        return d


@dataclass
class TrainingRun:
    run_id: str
    model_name: str = "Codix"
    base_version: str = "0.1"
    stage: TrainingStage = TrainingStage.COLLECT
    dataset_size: int = 0
    eval_score: float | None = None
    passed: bool = False
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        d = self.__dict__.copy()
        d["stage"] = self.stage.value
        return d
