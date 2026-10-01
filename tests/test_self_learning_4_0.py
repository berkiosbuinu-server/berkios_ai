import tempfile
from pathlib import Path

from berkios.learning.corrections import SelfLearningCorrectionLoop


def test_capture_requires_successful_verification():
    with tempfile.TemporaryDirectory() as d:
        loop = SelfLearningCorrectionLoop(Path(d))
        try:
            loop.capture(message="x", verification={"success": False})
        except ValueError:
            pass
        else:
            raise AssertionError("failed verification must not be learned")


def test_capture_and_recall():
    with tempfile.TemporaryDirectory() as d:
        loop = SelfLearningCorrectionLoop(Path(d))
        item = loop.capture(
            message="ImportError missing module",
            error_id="e1",
            run_id="r1",
            files=["src/app.py"],
            symbols=["main"],
            diagnosis={"cause": "dependency"},
            proposal={"change": "add import"},
            verification={"success": True},
        )
        assert item.correction_id
        found = loop.relevant(message="ImportError", files=["src/app.py"])
        assert found
        assert found[0]["error_id"] == "e1"
