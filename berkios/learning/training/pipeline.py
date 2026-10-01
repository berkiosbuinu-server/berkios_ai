from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
import uuid

from .models import (
    CuratedExample, ExampleStatus, TrainingRun, TrainingStage
)


class CodixTrainingPipeline:
    """Pipeline de préparation/évaluation; aucun entraînement implicite."""

    def __init__(self):
        self.examples: dict[str, CuratedExample] = {}
        self.runs: dict[str, TrainingRun] = {}

    def ingest(self, raw: dict):
        example = CuratedExample(
            example_id=raw["example_id"],
            task=raw.get("task", ""),
            input_data=raw.get("input_data", {}),
            output_data=raw.get("output_data", {}),
            provider=raw.get("provider"),
            model=raw.get("model"),
            feedback=raw.get("feedback"),
            score=raw.get("score"),
            tags=raw.get("tags", []),
        )
        self.examples[example.example_id] = example
        return example

    def review(self, example_id, approved: bool, redactions=None, tags=None):
        example = self.examples[example_id]
        example.status = (
            ExampleStatus.REVIEWED if approved
            else ExampleStatus.REJECTED
        )
        if approved:
            example.redactions = list(redactions or [])
            example.tags = list(tags or example.tags)
        return example

    def approve_for_training(self, example_id):
        example = self.examples[example_id]
        if example.status != ExampleStatus.REVIEWED:
            raise ValueError("example must be reviewed before approval")
        example.status = ExampleStatus.APPROVED
        return example

    def start(self, model_name="Codix", base_version="0.1"):
        run = TrainingRun(
            run_id=str(uuid.uuid4()),
            model_name=model_name,
            base_version=base_version,
            stage=TrainingStage.CURATE,
        )
        self.runs[run.run_id] = run
        return run

    def build_dataset(self, run_id):
        run = self.runs[run_id]
        selected = [
            e for e in self.examples.values()
            if e.status == ExampleStatus.APPROVED
        ]
        run.dataset_size = len(selected)
        run.stage = TrainingStage.EVALUATE
        return selected

    def record_eval(self, run_id, score, passed):
        run = self.runs[run_id]
        run.eval_score = float(score)
        run.passed = bool(passed)
        run.stage = TrainingStage.EXPORT if passed else TrainingStage.CURATE
        return run

    def export_jsonl(self, run_id, destination):
        run = self.runs[run_id]
        selected = self.build_dataset(run_id)
        path = Path(destination)
        path.write_text(
            "".join(
                json.dumps(e.to_dict(), ensure_ascii=False) + "\n"
                for e in selected
            ),
            encoding="utf-8",
        )
        run.artifacts.append(str(path))
        run.stage = TrainingStage.EXPORT
        return str(path)

    def promote(self, run_id):
        run = self.runs[run_id]
        if not run.passed:
            raise ValueError("training run did not pass evaluation")
        run.stage = TrainingStage.PROMOTE
        return run
