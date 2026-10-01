import tempfile
from pathlib import Path
from berkios.engineeringloop import EngineeringLoop

class FakeExplainer:
    def explain_file(self,p): return type("R",(),{"to_dict":lambda s:{"target":p}})()

class FakeExplorer:
    def explore_file(self,p): return type("R",(),{"to_dict":lambda s:{"target":p}})()

class FakePlanner:
    def plan(self,t,r):
        return type("R",(),{"approval_required":True,"to_dict":lambda s:{"target":t}})()

class FakeRepair:
    def prepare(self,**kw):
        return type("R",(),{"to_dict":lambda s:kw})()

def test_engineering_cycle():
    with tempfile.TemporaryDirectory() as d:
        p=Path(d); (p/"app.py").write_text("x=1\n",encoding="utf-8")
        loop=EngineeringLoop(
            p, explainer=FakeExplainer(), explorer=FakeExplorer(),
            change_planner=FakePlanner(), repair=FakeRepair())
        run=loop.start("app.py","modifier x")
        assert run.result=="pending"
        assert any(s.state=="waiting_approval" for s in run.states)
        run=loop.approve(run)
        run=loop.record_verification(run,False,"SyntaxError", "syntax")
        assert run.result=="repair_required"
        assert run.repair_context
