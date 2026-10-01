from berkios.learning.manager import CodixTrainingManager, ManagerState

def worker(run, progress):
    progress(run.run_id,.5,"DATASET_READY")
    progress(run.run_id,.8,"TRAINING",{"loss":.2})
    progress(run.run_id,.95,"VALIDATING",{"validation_score":.92})
    return {"validated":True,"version":"codix-0.2","metrics":{"validation_score":.92}}

def test_lifecycle(tmp_path):
    m=CodixTrainingManager(tmp_path)
    r=m.create(dataset_id="codix",dataset_version="0.1",base_version="codix-0.1")
    result=m.start_background(r.run_id,worker).result(timeout=3)
    assert result.state==ManagerState.READY_TO_PROMOTE
    m.promote(r.run_id,version="codix-0.2",artifact="adapter",score=.92)
    assert m.get(r.run_id).state==ManagerState.PROMOTED

def test_cancel(tmp_path):
    m=CodixTrainingManager(tmp_path)
    r=m.create(dataset_id="x",dataset_version="1")
    assert m.cancel(r.run_id).state==ManagerState.CANCELLED
