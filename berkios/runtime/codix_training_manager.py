from berkios.learning.manager import CodixTrainingManager
class RuntimeCodixTrainingManager:
    def __init__(self, root=".berkios/training_manager", max_workers=1):
        self.manager=CodixTrainingManager(root,max_workers)
    def create(self,**kw): return self.manager.create(**kw)
    def get(self,id): return self.manager.get(id)
    def start_background(self,id,worker): return self.manager.start_background(id,worker)
    def cancel(self,id): return self.manager.cancel(id)
    def promote(self,id,**kw): return self.manager.promote(id,**kw)
    def versions(self): return self.manager.versions()
