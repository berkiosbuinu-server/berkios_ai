from berkios.agentcontext import AgentContextEngine

class RuntimeAgentContext:
    def __init__(self):
        self.engine=AgentContextEngine()
    def build(self,**kwargs):
        return self.engine.build(**kwargs).to_dict()
