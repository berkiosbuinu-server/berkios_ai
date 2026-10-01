from berkios.learning.teacher import MultiTeacherEngine, TeacherDataBuilder


def make(builder, provider, output):
    return builder.normalize(
        provider=provider,
        model=None,
        task="fix bug",
        input_context="project context",
        output=output,
        tests=["pytest"],
    )


def test_unique_agreement_group():
    b = TeacherDataBuilder()
    engine = MultiTeacherEngine()

    a = make(b, "openai", "solution")
    c = make(b, "claude", "solution")
    d = make(b, "gemini", "different")

    result = engine.compare("fix bug", [a, c, d])
    assert result.selected_sample_id in {a.sample_id, c.sample_id}
    assert len(result.agreement_groups) == 2


def test_tie_does_not_select():
    b = TeacherDataBuilder()
    engine = MultiTeacherEngine()

    a = make(b, "openai", "A")
    c = make(b, "claude", "B")

    result = engine.compare("fix bug", [a, c])
    assert result.selected_sample_id is None


def test_synthesis_remains_review_candidate():
    b = TeacherDataBuilder()
    engine = MultiTeacherEngine()

    a = make(b, "openai", "A")
    c = make(b, "claude", "B")

    result = engine.compare("fix bug", [a, c])
    engine.synthesize(result, synthesis="A+B", rationale="Human-approved synthesis")

    candidate = engine.to_candidate(result)
    assert candidate is not None
    assert candidate.teacher_provider == "multi-teacher"
    assert candidate.consent_required is True
    assert candidate.evaluation["requires_human_review"] is True
