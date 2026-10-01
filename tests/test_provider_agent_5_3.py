from pathlib import Path

from berkios.runtime.app import AgentRuntime
from berkios.providers.agent_decision import AgentDecision


class FakeProvider:
    name = "fake"
    configured = True

    def decide(self, request, context):
        return AgentDecision(
            action="analyze",
            reason="test provider",
            metadata={"request": request},
        )


def test_provider_agent_uses_selected_provider(tmp_path):
    runtime = AgentRuntime(tmp_path)
    runtime.providers.register(FakeProvider())
    runtime.providers.select("fake")

    agent = runtime.create_provider_agent()
    result = agent.loop("Analyse ce projet")

    assert result.status == "waiting"
    assert result.decisions
    assert result.decisions[0]["decision"]["action"] == "analyze"
    assert runtime.providers.selected == "fake"
