from pathlib import Path
from berkios.learning.trainer import CodixTrainerEngine, TrainerConfig, SimulatedLocalAdapter, TrainerStatus

def test_checkpointed_training(tmp_path):
    engine=CodixTrainerEngine(tmp_path/"runs")
    result=engine.train(
        run_id="r1",
        examples=[{"input":"a"},{"input":"b"},{"input":"c"},{"input":"d"}],
        backend=SimulatedLocalAdapter(),
        config=TrainerConfig(epochs=2,batch_size=2,checkpoint_every_steps=1,
                             output_dir=str(tmp_path/"models"))
    )
    assert result.status == TrainerStatus.COMPLETED
    assert result.steps == 4
    assert Path(result.artifact).exists()

def test_resume(tmp_path):
    engine=CodixTrainerEngine(tmp_path/"runs")
    cfg=TrainerConfig(epochs=3,batch_size=1,checkpoint_every_steps=1,
                      output_dir=str(tmp_path/"models"))
    first=engine.train(run_id="r2",examples=[{"x":1},{"x":2}],backend=SimulatedLocalAdapter(),config=cfg)
    cp=tmp_path/"runs"/"r2.checkpoint.json"
    assert cp.exists()
    data=cp.read_text(encoding="utf-8")
    import json
    artifact=json.loads(data)["artifact"]
    second=engine.train(run_id="r2-resume",examples=[{"x":1},{"x":2}],backend=SimulatedLocalAdapter(),
                        config=cfg,resume_from=artifact)
    assert second.status == TrainerStatus.COMPLETED

def test_empty_dataset_fails(tmp_path):
    engine=CodixTrainerEngine(tmp_path)
    r=engine.train(run_id="empty",examples=[],backend=SimulatedLocalAdapter(),config=TrainerConfig())
    assert r.status == TrainerStatus.FAILED
