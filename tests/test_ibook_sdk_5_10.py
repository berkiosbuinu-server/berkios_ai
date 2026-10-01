from berkios.ibook.agent import IBookAgentBridge
from berkios.sdk.live import IBookAgentClient


def test_sdk_symbols():
    client = IBookAgentClient()
    bridge = IBookAgentBridge()
    assert client.base_url.startswith("http://")
    assert hasattr(bridge, "ask")
    assert hasattr(bridge, "status")
    assert hasattr(bridge, "events")
    assert hasattr(bridge, "pause")
    assert hasattr(bridge, "cancel")
