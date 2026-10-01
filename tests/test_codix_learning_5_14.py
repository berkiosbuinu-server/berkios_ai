from berkios.learning import LearningStore,LearningExample
from berkios.models import CodixProfile,ModelBackend

def test_codix_provider_neutral():
    p=CodixProfile(provider="openai",model="provider-model")
    assert p.name=="Codix" and p.domain=="software-engineering"
    assert p.backend==ModelBackend.PROVIDER

def test_learning_requires_consent(tmp_path):
    s=LearningStore(tmp_path); e=LearningExample(task="fix")
    try: s.add(e); assert False
    except PermissionError: pass
    c=s.consent(); c.grant(["validated_corrections"]); s.set_consent(c)
    s.add(e); assert len(s.list())==1
