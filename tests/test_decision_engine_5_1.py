from berkios.decision import DecisionEngine

def test_change():
    d=DecisionEngine().decide("modifie cette fonction",{"graph_impact":{"risk_level":"medium"}},"app.py")
    assert d.selected_action=="analyze_and_propose_change"
    assert d.constraints

def test_explain():
    d=DecisionEngine().decide("explique ce code",target="app.py")
    assert d.selected_action=="explain"
