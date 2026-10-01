from berkios.actionplan import ActionPlanner


class D:
    action = "analyze_and_propose_change"
    objective = "Corriger"
    rationale = "Erreur détectée"


def test_action_plan_requires_approval_for_change():
    plan = ActionPlanner().plan(D(), "Corrige", {"active_file": "app.py"})
    assert plan.approval_required is True
    assert plan.verification_required is True
    assert [a.id for a in plan.actions] == ["a1", "a2", "a3", "a4"]
    assert plan.actions[2].requires_approval is True
