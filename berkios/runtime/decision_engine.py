from berkios.decision import DecisionEngine

class RuntimeDecisionEngine:
    def __init__(self): self.engine=DecisionEngine()
    def decide(self,**kwargs): return self.engine.decide(**kwargs).to_dict()
