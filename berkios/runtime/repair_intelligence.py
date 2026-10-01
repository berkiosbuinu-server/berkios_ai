from berkios.repairintel import RepairIntelligence

class RuntimeRepairIntelligence:
    def __init__(self,workspace):
        self.engine=RepairIntelligence(workspace)
    def prepare(self,**kwargs):
        return self.engine.prepare(**kwargs).to_dict()
