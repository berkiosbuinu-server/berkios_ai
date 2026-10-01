from berkios.agentcontext import AgentContextEngine

def test_context_priority():
    e=AgentContextEngine()
    c=e.build(
        request="modifier",
        target="app.py",
        active_file="app.py",
        selection="return x",
        diagnostics=["error"],
        snapshot={
            "graph_impact":{"risk_level":"high"},
            "project_understanding":{"summary":"project"},
            "code_explanation":{"purpose":"role"},
        },
    )
    assert c.sections[0].name in ("selection","request","diagnostics")
    assert c.constraints
    assert c.summary
