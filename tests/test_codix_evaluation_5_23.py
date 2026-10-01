from berkios.learning.evaluation import CodixEvaluator, CodixModelRegistry
from berkios.learning.evaluation.models import EvaluationCase, EvaluationResult, ModelRecord

def test_evaluation_and_compare():
    e=CodixEvaluator()
    cases=[EvaluationCase("1","echo","a","ok"),EvaluationCase("2","echo","b","ok")]
    r=e.evaluate(model_version="new",cases=cases,predict=lambda c:"ok")
    b=EvaluationResult("old",.90,True,2,2,{"mean_score":.90})
    assert r.passed
    assert e.compare(r,b)["passed"]

def test_registry_only_promotes_validated(tmp_path):
    reg=CodixModelRegistry(tmp_path)
    reg.register(ModelRecord("0.2","adapter","validated",.92,"0.1"))
    assert reg.promote("0.2").status=="active"
    assert reg.active=="0.2"
