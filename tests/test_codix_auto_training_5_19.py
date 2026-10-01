from berkios.learning.training_auto import AutoTrainingConfig, AutoTrainingPipeline, TrainingStatus

def trainer(manifest, root, config):
    return {"artifact": str(root/"codix_adapter.bin"), "metrics": {"validation_score": 0.91}}

def test_auto_training_with_gates(tmp_path):
    p=AutoTrainingPipeline(tmp_path, AutoTrainingConfig(
        min_quality_score=0.8, min_validation_score=0.8,
        require_consent=True, require_human_approval=True
    ))
    p.register_trainer(trainer)
    run=p.start(
        dataset_id="codix", dataset_version="0.1", base_model="base",
        examples=[{"quality_score":0.9},{"quality_score":0.95}],
        consent=True, human_approved=True, baseline_score=0.85
    )
    assert run.status == TrainingStatus.VALIDATING
    p.promote(run)
    assert run.status == TrainingStatus.PROMOTED

def test_no_consent_never_trains(tmp_path):
    p=AutoTrainingPipeline(tmp_path)
    called=[]
    p.register_trainer(lambda *a: called.append(1) or {"metrics":{"validation_score":1}})
    run=p.start(dataset_id="x",dataset_version="1",base_model="b",
                examples=[{"quality_score":1}],consent=False,human_approved=True)
    assert run.status == TrainingStatus.REJECTED
    assert not called

def test_regression_is_rejected(tmp_path):
    p=AutoTrainingPipeline(tmp_path, AutoTrainingConfig(
        min_quality_score=0.5,min_validation_score=0.5,max_quality_drop=0.02,
        require_consent=False,require_human_approval=False
    ))
    p.register_trainer(lambda *a: {"metrics":{"validation_score":0.70}})
    run=p.start(dataset_id="x",dataset_version="1",base_model="b",
                examples=[{"quality_score":1}],consent=True,human_approved=True,
                baseline_score=0.90)
    assert run.status == TrainingStatus.REJECTED
