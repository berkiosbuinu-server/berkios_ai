from berkios.learning import LearningConsent,LearningExample,LearningStore
from berkios.models import CodixProfile,ModelRegistry
class RuntimeCodixLearning:
    def __init__(self,runtime,workspace=None):
        self.runtime=runtime; self.workspace=workspace or getattr(runtime,"workspace",".")
        self.models=ModelRegistry(); self.models.register(CodixProfile())
        self.store=LearningStore(self.workspace)
    def codix(self): return self.models.get("Codix")
    def consent(self): return self.store.consent()
    def enable_learning(self,scope):
        c=self.store.consent(); c.grant(scope); self.store.set_consent(c); return c
    def disable_learning(self):
        c=self.store.consent(); c.revoke(); self.store.set_consent(c); return c
    def add_example(self,**kwargs): return self.store.add(LearningExample(**kwargs))
    def dataset(self): return self.store.list()
    def export_dataset(self,destination): return str(self.store.export_jsonl(destination))
