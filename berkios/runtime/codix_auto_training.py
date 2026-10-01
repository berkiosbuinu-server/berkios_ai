from __future__ import annotations
from berkios.learning.training_auto import AutoTrainingPipeline, AutoTrainingConfig

class RuntimeCodixAutoTraining:
    def __init__(self, root=".berkios/auto_training", config=None):
        self.pipeline=AutoTrainingPipeline(root, config or AutoTrainingConfig())
    def register_trainer(self, trainer):
        self.pipeline.register_trainer(trainer)
    def start(self, **kwargs):
        return self.pipeline.start(**kwargs)
    def promote(self, run):
        return self.pipeline.promote(run)
