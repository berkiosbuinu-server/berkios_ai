import json
from berkios.decision.provider import ProviderDecisionIntegration
from berkios.providers.base import AIProvider

class Fake(AIProvider):
    name="fake"
    def decide_structured(self, request, context):
        return {
            "objective":"tester",
            "interpretation":"test",
            "evidence":["e1"],
            "constraints":["c1"],
            "actions":[{
                "action":"analyze",
                "reason":"r",
                "prerequisites":[],
                "approval_required":False,
                "verification_required":False
            }],
            "selected_action":"analyze",
            "rationale":"ok",
            "uncertainty":[]
        }

class E:
    def __init__(self):
        self.providers={"fake":Fake()}
        self.selected="fake"
    def current(self): return self.providers[self.selected]

def test_provider_decision_normalization():
    d=ProviderDecisionIntegration().decide(E(),"x",{})
    assert d.selected_action=="analyze"
    assert d.actions[0].approval_required is False
