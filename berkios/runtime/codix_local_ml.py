from __future__ import annotations
from berkios.learning.trainer.local_ml import LocalMLBackend, environment_report

class RuntimeCodixLocalML:
    def environment(self):
        return environment_report()

    def create_backend(self, model_name_or_path, output_dir):
        return LocalMLBackend(model_name_or_path, output_dir)
