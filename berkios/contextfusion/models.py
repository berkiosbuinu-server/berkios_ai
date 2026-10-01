from dataclasses import dataclass, asdict, field

@dataclass
class ProjectContextSnapshot:
    workspace: str
    request: str
    project_understanding: dict = field(default_factory=dict)
    code_explanation: dict = field(default_factory=dict)
    code_exploration: dict = field(default_factory=dict)
    graph_impact: dict = field(default_factory=dict)
    change_plan: dict = field(default_factory=dict)
    verification: dict = field(default_factory=dict)
    repair_context: dict = field(default_factory=dict)
    active_file: str | None = None
    selection: str | None = None
    diagnostics: list = field(default_factory=list)
    relevant_memory: list = field(default_factory=list)
    summary: str = ""
    def to_dict(self): return asdict(self)
