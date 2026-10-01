from berkios.actionplan import ActionPlanner, CapabilityResolver


class D:
    action = "analyze_and_propose_change"
    objective = "Corriger"
    rationale = "test"


def test_resolution_keeps_approval_separate():
    plan = ActionPlanner().plan(D(), "Corrige", {"active_file": "app.py"})
    matches = CapabilityResolver().resolve(plan)
    assert len(matches) == 4
    assert matches[2].requires_permission is True
    assert matches[2].available is True
