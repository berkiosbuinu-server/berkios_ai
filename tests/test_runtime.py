from berkios.runtime.app import create_runtime

def test_runtime_boots(tmp_path):
    rt = create_runtime(tmp_path)
    assert "local" in rt.providers.list()
    assert "filesystem.read" in rt.tools.list()

def test_context(tmp_path):
    rt = create_runtime(tmp_path)
    rt.context.update(active_file="main.py", cursor={"line":1,"column":2})
    assert rt.context.snapshot()["active_file"] == "main.py"

def test_run(tmp_path):
    rt = create_runtime(tmp_path)
    result = rt.create_loop("Analyse ce projet").run()
    assert result["state"] == "completed"
    assert result["run_id"]
