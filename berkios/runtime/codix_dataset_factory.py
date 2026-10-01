from __future__ import annotations

from pathlib import Path
from berkios.learning.dataset_factory import CodixDatasetFactory


class RuntimeCodixDatasetFactory:
    """Runtime facade for creating versioned Codix datasets."""

    def __init__(self, root: str | Path = ".berkios/datasets", seed: int = 42):
        self.factory = CodixDatasetFactory(root=root, seed=seed)

    def build(self, candidates, **kwargs):
        return self.factory.build(candidates, **kwargs)

    def export_jsonl(self, dataset, destination=None):
        return self.factory.export_jsonl(dataset, destination)

    def export_manifest(self, dataset, destination=None):
        return self.factory.export_manifest(dataset, destination)
