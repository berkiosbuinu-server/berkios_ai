from dataclasses import dataclass,field
from typing import Any
@dataclass
class EvalResult:
    model:str; task:str; score:float; passed:bool; metrics:dict[str,Any]=field(default_factory=dict)
class EvalRegistry:
    def __init__(self): self.results=[]
    def record(self,result): self.results.append(result); return result
    def for_model(self,model): return [x for x in self.results if x.model==model]
