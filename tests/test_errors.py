from berkios.errors.manager import ErrorManager

TRACE = """
Traceback (most recent call last):
  File "main.py", line 12, in run
    x = value()
TypeError: object is not callable
"""

def test_parse_and_diagnose():
    manager = ErrorManager()
    events = manager.ingest_python(TRACE)
    assert events
    assert any(e.kind.value == "type" for e in events)
    diagnosis = manager.diagnose(events[-1].id)
    assert diagnosis["suggested_actions"]

def test_command_error():
    manager = ErrorManager()
    events = manager.ingest_command(["python", "test.py"], 1, "", "AssertionError: boom")
    assert events
    assert events[-1].kind.value == "test"
