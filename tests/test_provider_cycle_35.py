from pathlib import Path
from berkios.runtime.provider_cycle import ProviderDrivenCycle

class FakeProvider:
    def decide(self, request, context):
        return {
            "action": "propose",
            "reason": "test",
            "proposal": {"files": ["a.py"]},
        }

def test_provider_decision(tmp_path: Path):
    (tmp_path / "a.py").write_text("class A: pass\n", encoding="utf-8")
    cycle = ProviderDrivenCycle(tmp_path, provider=FakeProvider())
    decision = cycle.decide("modify A", {})
    assert decision.action == "propose"
    assert decision.proposal["files"] == ["a.py"]
