from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DatasetSplit(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


@dataclass
class DatasetExample:
    example_id: str
    task: str
    input_text: str
    target_text: str
    split: DatasetSplit
    language: str | None = None
    task_type: str | None = None
    difficulty: str | None = None
    tags: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    quality_score: float | None = None
    created_at: str = field(default_factory=utc_now)


@dataclass
class CodixDataset:
    dataset_id: str
    version: str
    examples: list[DatasetExample] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def by_split(self, split: DatasetSplit) -> list[DatasetExample]:
        return [e for e in self.examples if e.split == split]
