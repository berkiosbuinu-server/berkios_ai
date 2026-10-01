from berkios.runtime.app import create_runtime

def test_run_lifecycle(tmp_path):
    rt = create_runtime(tmp_path)
    result = rt.create_loop("Analyse le projet").run()
    assert result["state"] == "completed"
    assert result["run_id"] in rt.runs

def test_context_sync(tmp_path):
    rt = create_runtime(tmp_path)
    rt.context.update(active_file="src/main.py")
    assert rt.context.snapshot()["active_file"] == "src/main.py"

def test_review_api_model(tmp_path):
    rt = create_runtime(tmp_path)
    assert rt.review.list() == []
