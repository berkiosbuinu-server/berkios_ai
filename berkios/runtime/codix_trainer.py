from __future__ import annotations
from berkios.learning.trainer import CodixTrainerEngine, TrainerConfig

class RuntimeCodixTrainer:
    def __init__(self, root=".berkios/trainer_runs"):
        self.engine=CodixTrainerEngine(root)

    def train(self, **kwargs):
        return self.engine.train(**kwargs)
