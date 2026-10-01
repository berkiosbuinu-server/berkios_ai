from berkios.runtime.app import create_runtime

def test_correction_memory(tmp_path):
    rt=create_runtime(tmp_path)
    events=rt.errors.ingest_command(
        ["pytest"],1,"","TypeError: object is not callable","pytest")
    error=events[-1]
    item=rt.corrections.remember(
        error,
        diagnosis={"summary":"Valeur appelée comme fonction"},
        files=["src/service.py"],
        verification={"ok":True},
        run_id="run-1",
        git={"commit":"abc123","branch":"main"}
    )
    assert item["status"]=="corrected"
    matches=rt.corrections.search(error)
    assert matches[0]["git"]["commit"]=="abc123"
    assert rt.corrections.recall(error)["matches"]
