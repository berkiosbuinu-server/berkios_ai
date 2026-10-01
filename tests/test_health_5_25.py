import json
from berkios.api.server import Handler

def test_health_route_exists():
    source = Handler.do_GET.__code__
    assert source.co_code
    import inspect
    text = inspect.getsource(Handler.do_GET)
    assert 'path == "/health"' in text
    assert '"berkios-api"' in text
