from berkios.runtime.app import create_runtime

def test_index_and_correlate(tmp_path):
    (tmp_path/"main.py").write_text(
        "def calculate(value):\n    return value()\n\ncalculate(42)\n",
        encoding="utf-8")
    rt = create_runtime(tmp_path)
    index = rt.code_intelligence.project()
    assert index["main.py"]["symbols"][0]["name"] == "calculate"

    trace = '''Traceback (most recent call last):
  File "main.py", line 2, in calculate
    return value()
TypeError: object is not callable
'''
    events = rt.errors.ingest_python(trace)
    event = next(e for e in events if e.kind.value == "type")
    analysis = rt.code_intelligence.analyze_error(event.id)
    assert analysis["correlation"]["symbol"]["name"] == "calculate"
    assert "return value()" in analysis["correlation"]["nearby_code"]
