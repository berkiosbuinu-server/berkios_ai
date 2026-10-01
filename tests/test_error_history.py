from berkios.runtime.app import create_runtime

def test_error_history_persists(tmp_path):
    rt=create_runtime(tmp_path)
    events=rt.errors.ingest_command(
        ["pytest","tests/test_x.py"],1,"","AssertionError: expected 1 got 2","pytest")
    assert events
    history=rt.error_history.list()
    assert history
    assert history[-1]["kind"]=="test"

def test_similar_error(tmp_path):
    rt=create_runtime(tmp_path)
    events=rt.errors.ingest_command(["pytest"],1,"","AssertionError: expected 1 got 2","pytest")
    matches=rt.error_history.similar(events[-1])
    assert matches
