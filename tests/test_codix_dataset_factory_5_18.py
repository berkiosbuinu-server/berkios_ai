from berkios.learning.dataset_factory import CodixDatasetFactory
from berkios.learning.dataset_factory.models import DatasetSplit


def test_build_dedup_and_split(tmp_path):
    factory = CodixDatasetFactory(tmp_path, seed=7)
    candidates = [
        {
            "sample_id": "a",
            "task": "fix parser",
            "input_context": "def parse(x):",
            "teacher_output": "return x",
            "language": "python",
            "task_type": "debugging",
            "difficulty": "easy",
            "provenance": {"provider": "openai"},
            "quality_score": 0.9,
        },
        {
            "sample_id": "a-duplicate",
            "task": "fix parser",
            "input_context": "def parse(x):",
            "teacher_output": "return x",
        },
        {
            "sample_id": "b",
            "task": "write test",
            "input_context": "pytest",
            "teacher_output": "def test_x(): pass",
        },
        {
            "sample_id": "c",
            "task": "explain code",
            "input_context": "function foo() {}",
            "teacher_output": "It is a function.",
        },
    ]

    ds = factory.build(candidates, train_ratio=0.5, validation_ratio=0.25, test_ratio=0.25)
    assert len(ds.examples) == 3
    assert len(ds.by_split(DatasetSplit.TRAIN)) == 1
    assert len(ds.by_split(DatasetSplit.VALIDATION)) == 1
    assert len(ds.by_split(DatasetSplit.TEST)) == 1


def test_exports(tmp_path):
    factory = CodixDatasetFactory(tmp_path)
    ds = factory.build([{
        "sample_id": "x",
        "task": "debug",
        "input_context": "def f(): pass",
        "teacher_output": "def f(): return 1",
    }])

    jsonl = factory.export_jsonl(ds)
    manifest = factory.export_manifest(ds)
    assert jsonl.exists()
    assert manifest.exists()
