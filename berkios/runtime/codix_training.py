from __future__ import annotations
from berkios.learning.training import CodixTrainingPipeline


class RuntimeCodixTraining:
    def __init__(self, runtime):
        self.runtime = runtime
        self.pipeline = CodixTrainingPipeline()

    def ingest(self, raw):
        return self.pipeline.ingest(raw)

    def review(self, example_id, approved, redactions=None, tags=None):
        return self.pipeline.review(example_id, approved, redactions, tags)

    def approve(self, example_id):
        return self.pipeline.approve_for_training(example_id)

    def start(self, model_name="Codix", base_version="0.1"):
        return self.pipeline.start(model_name, base_version)

    def build_dataset(self, run_id):
        return self.pipeline.build_dataset(run_id)

    def evaluate(self, run_id, score, passed):
        return self.pipeline.record_eval(run_id, score, passed)

    def export(self, run_id, destination):
        return self.pipeline.export_jsonl(run_id, destination)

    def promote(self, run_id):
        return self.pipeline.promote(run_id)
