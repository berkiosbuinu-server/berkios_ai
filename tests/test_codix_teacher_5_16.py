from pathlib import Path

from berkios.learning.teacher import TeacherDataBuilder


def test_normalize_and_compare(tmp_path: Path):
    builder = TeacherDataBuilder(tmp_path)

    a = builder.normalize(
        provider="provider-a",
        model="teacher-a",
        task="fix bug",
        input_context="context",
        output="same answer",
    )
    b = builder.normalize(
        provider="provider-b",
        model="teacher-b",
        task="fix bug",
        input_context="context",
        output="same answer",
    )

    assert a.sample_id
    session = builder.compare(task="fix bug", samples=[a, b])
    assert session.providers == ["provider-a", "provider-b"]
    assert session.consensus == "same answer"


def test_divergence_has_no_automatic_consensus(tmp_path: Path):
    builder = TeacherDataBuilder(tmp_path)

    a = builder.normalize(
        provider="provider-a",
        model=None,
        task="review",
        input_context="context",
        output="answer A",
    )
    b = builder.normalize(
        provider="provider-b",
        model=None,
        task="review",
        input_context="context",
        output="answer B",
    )

    session = builder.compare(task="review", samples=[a, b])
    assert session.consensus is None
