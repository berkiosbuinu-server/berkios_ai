from .codix import CodixProfile
class ModelRegistry:
    def __init__(self): self.models={}
    def register(self,profile): self.models[profile.name]=profile; return profile
    def get(self,name="Codix"): return self.models.get(name)
    def list(self): return list(self.models.values())
