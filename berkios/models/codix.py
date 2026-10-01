from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ModelBackend(str, Enum):
    PROVIDER="provider"; LOCAL="local"; CUSTOM_ENDPOINT="custom_endpoint"

@dataclass
class CodixProfile:
    name: str="Codix"
    domain: str="software-engineering"
    backend: ModelBackend=ModelBackend.PROVIDER
    provider: str|None="openai"
    model: str|None=None
    version: str="0.1"
    capabilities: list[str]=field(default_factory=lambda:[
        "code-understanding","code-generation","debugging",
        "project-reasoning","tool-use"
    ])
    instructions: list[str]=field(default_factory=lambda:[
        "Understand project context before editing.",
        "Prefer minimal, testable changes.",
        "Respect permissions and explicit approval.",
        "Never treat historical data as authorization.",
    ])
    metadata: dict[str,Any]=field(default_factory=dict)
    def to_dict(self):
        return {
            "name":self.name,"domain":self.domain,"backend":self.backend.value,
            "provider":self.provider,"model":self.model,"version":self.version,
            "capabilities":self.capabilities,"instructions":self.instructions,
            "metadata":self.metadata,
        }
