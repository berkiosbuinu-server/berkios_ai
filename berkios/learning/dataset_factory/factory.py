from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Iterable

from .models import CodixDataset, DatasetExample, DatasetSplit


class CodixDatasetFactory:
    """Build curated, deterministic Codix datasets from approved candidates."""

    def __init__(self, root: str | Path = ".berkios/datasets", seed: int = 42):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.seed = seed

    def _fingerprint(self, task: str, input_text: str, target_text: str) -> str:
        raw = f"{task}\0{input_text}\0{target_text}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:24]

    def _infer_language(self, text: str) -> str | None:
        markers = {
            "python": ("def ", "import ", "from ", "pytest", "asyncio"),
            "javascript": ("const ", "let ", "function ", "=>", "npm"),
            "typescript": ("interface ", "type ", ": string", ": number"),
            "java": ("public class ", "public static void", "System.out"),
            "rust": ("fn ", "let mut ", "cargo", "impl "),
            "go": ("package main", "func ", "go.mod"),
        }
        scores = {
            lang: sum(1 for marker in ms if marker in text)
            for lang, ms in markers.items()
        }
        if not scores:
            return None
        lang, score = max(scores.items(), key=lambda x: x[1])
        return lang if score else None

    def _dedupe(self, candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        seen = set()
        result = []
        for c in candidates:
            fp = self._fingerprint(
                str(c.get("task", "")),
                str(c.get("input_text", c.get("input_context", ""))),
                str(c.get("target_text", c.get("teacher_output", ""))),
            )
            if fp in seen:
                continue
            seen.add(fp)
            item = dict(c)
            item["_fingerprint"] = fp
            result.append(item)
        return result

    def build(
        self,
        candidates: Iterable[dict[str, Any]],
        *,
        dataset_id: str = "codix",
        version: str = "0.1",
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.1,
        metadata: dict[str, Any] | None = None,
    ) -> CodixDataset:
        total = train_ratio + validation_ratio + test_ratio
        if abs(total - 1.0) > 1e-9:
            raise ValueError("Split ratios must sum to 1.0")

        items = self._dedupe(candidates)
        rng = random.Random(self.seed)
        rng.shuffle(items)

        n = len(items)
        ratios = [train_ratio, validation_ratio, test_ratio]
        counts = [int(n * r) for r in ratios]
        # Allocate remainder by largest fractional part (stable split order).
        remainder = n - sum(counts)
        order = sorted(range(3), key=lambda i: (n * ratios[i] - counts[i], -i), reverse=True)
        for i in order[:remainder]:
            counts[i] += 1
        # When enough examples exist, avoid silently emptying a requested split.
        for i, ratio in enumerate(ratios):
            if ratio > 0 and n >= sum(r > 0 for r in ratios) and counts[i] == 0:
                donor = max((j for j in range(3) if counts[j] > 1), key=lambda j: counts[j], default=None)
                if donor is not None:
                    counts[donor] -= 1
                    counts[i] += 1
        train_end = counts[0]
        val_end = train_end + counts[1]

        examples: list[DatasetExample] = []
        for i, c in enumerate(items):
            if i < train_end:
                split = DatasetSplit.TRAIN
            elif i < val_end:
                split = DatasetSplit.VALIDATION
            else:
                split = DatasetSplit.TEST

            inp = str(c.get("input_text", c.get("input_context", "")))
            target = str(c.get("target_text", c.get("teacher_output", "")))
            quality = c.get("quality_score")
            if quality is not None:
                quality = float(quality)

            examples.append(
                DatasetExample(
                    example_id=c.get("example_id") or c.get("sample_id") or c["_fingerprint"],
                    task=str(c.get("task", "")),
                    input_text=inp,
                    target_text=target,
                    split=split,
                    language=c.get("language") or self._infer_language(inp + "\n" + target),
                    task_type=c.get("task_type"),
                    difficulty=c.get("difficulty"),
                    tags=list(c.get("tags", [])),
                    provenance=dict(c.get("provenance", {})),
                    quality_score=quality,
                )
            )

        return CodixDataset(
            dataset_id=dataset_id,
            version=version,
            examples=examples,
            metadata={
                **(metadata or {}),
                "seed": self.seed,
                "deduplicated_count": len(items),
                "split_ratios": {
                    "train": train_ratio,
                    "validation": validation_ratio,
                    "test": test_ratio,
                },
            },
        )

    def export_jsonl(self, dataset: CodixDataset, destination: str | Path | None = None) -> Path:
        path = Path(destination) if destination else self.root / f"{dataset.dataset_id}_{dataset.version}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for example in dataset.examples:
                f.write(json.dumps({
                    "example_id": example.example_id,
                    "task": example.task,
                    "input": example.input_text,
                    "target": example.target_text,
                    "split": example.split.value,
                    "language": example.language,
                    "task_type": example.task_type,
                    "difficulty": example.difficulty,
                    "tags": example.tags,
                    "provenance": example.provenance,
                    "quality_score": example.quality_score,
                }, ensure_ascii=False) + "\n")
        return path

    def export_manifest(self, dataset: CodixDataset, destination: str | Path | None = None) -> Path:
        path = Path(destination) if destination else self.root / f"{dataset.dataset_id}_{dataset.version}.manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "dataset_id": dataset.dataset_id,
            "version": dataset.version,
            "created_at": dataset.created_at,
            "metadata": dataset.metadata,
            "counts": {
                "train": len(dataset.by_split(DatasetSplit.TRAIN)),
                "validation": len(dataset.by_split(DatasetSplit.VALIDATION)),
                "test": len(dataset.by_split(DatasetSplit.TEST)),
                "total": len(dataset.examples),
            },
        }
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
