from berkios.learning.training import (
    CodixTrainingPipeline, ExampleStatus, TrainingStage
)


def test_training_pipeline_requires_review_and_approval():
    p = CodixTrainingPipeline()
    e = p.ingest({
        "example_id": "e1",
        "task": "fix bug",
        "input_data": {"code": "x"},
        "output_data": {"patch": "y"},
    })
    assert e.status == ExampleStatus.RAW

    p.review("e1", True, redactions=["secret"], tags=["python"])
    p.approve_for_training("e1")

    run = p.start()
    data = p.build_dataset(run.run_id)
    assert len(data) == 1
    assert run.stage == TrainingStage.EVALUATE


def test_failed_eval_cannot_promote():
    p = CodixTrainingPipeline()
    run = p.start()
    p.record_eval(run.run_id, 0.2, False)
    try:
        p.promote(run.run_id)
        assert False
    except ValueError:
        pass
