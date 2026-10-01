from berkios.graph.builder import ProjectGraphBuilder
from berkios.lsp.service import LSPService
from pathlib import Path
from ..agent.loop import AgentLoop
from ..context.live import LiveContext
from ..changes.engine import ChangeEngine
from ..changes.review import ChangeReview
from ..verification.engine import VerificationEngine
from ..memory.project import ProjectMemory
from ..memory.session import SessionMemory
from ..providers.local import LocalProvider
from ..providers.openai import OpenAIProvider
from ..decision.provider import ProviderDecisionIntegration
from ..providers.engine import ProviderEngine
from ..tools.registry import ToolRegistry
from ..tools.filesystem import FilesystemTool
from ..tools.search import SearchTool
from ..tools.git import GitTool
from ..tools.terminal import TerminalTool
from ..security.permissions import PermissionManager
from ..errors.manager import ErrorManager
from ..codeintel.index import CodeIndex
from ..codeintel.engine import CodeIntelligence
from ..memory.error_history import ErrorHistory
from ..memory.corrections import CorrectionMemory
from ..memory.semantic import SemanticMemory
from ..codeintel.semantic import ProjectSemanticAnalyzer

class AgentRuntime:
    def __init__(self, workspace="."):
        self.workspace = Path(workspace).resolve()
        self.context = LiveContext()
        self.error_history = ErrorHistory(self.workspace)
        self.errors = ErrorManager(self.error_history)
        self.corrections = CorrectionMemory(self.workspace)
        self.semantic_memory = SemanticMemory(self.workspace)
        self.code_index = CodeIndex(self.workspace)
        self.project_semantics = ProjectSemanticAnalyzer(self.workspace, self.code_index)
        self.code_intelligence = CodeIntelligence(self.workspace, self.code_index, self.errors)
        self.project_memory = ProjectMemory(self.workspace)
        self.session_memory = SessionMemory()
        self.providers = ProviderEngine()
        self.providers.register(LocalProvider())
        openai_provider = OpenAIProvider()
        if openai_provider.configured:
            self.providers.register(openai_provider)
            self.providers.select("openai")
        self.tools = ToolRegistry(PermissionManager())
        self.tools.register(FilesystemTool(self.workspace))
        self.tools.register(SearchTool(self.workspace))
        self.tools.register(GitTool(self.workspace))
        self.tools.register(TerminalTool(self.workspace))
        self.changes = ChangeEngine(self.workspace)
        self.review = ChangeReview()
        self.verification = VerificationEngine(self.workspace, self.errors)
        self.runs = {}
        self.decision_integration = ProviderDecisionIntegration()
        self._persistence = None
        self._execution_control = None
        self._runtime_states = {}
        self._approval_center = None
        self._live_bridge = None

    def create_loop(self, request, run_id=None):
        loop = AgentLoop(workspace=self.workspace, request=request, run_id=run_id,
            context=self.context, project_memory=self.project_memory,
            session_memory=self.session_memory, providers=self.providers,
            tools=self.tools, changes=self.changes, verification=self.verification,
            review=self.review)
        self.runs[loop.run_id] = loop
        return loop

    def get_run(self, run_id): return self.runs[run_id]

def create_runtime(workspace="."): return AgentRuntime(workspace)


# Berkios 2.7 graph/LSP integration helpers
def build_project_graph(self):
    builder = ProjectGraphBuilder(self.workspace)
    self.project_graph = builder.build()
    return self.project_graph

def graph_related(self, node_id: str):
    if not hasattr(self, "project_graph"):
        self.build_project_graph()
    return self.project_graph.related(node_id)

def lsp_service(self):
    if not hasattr(self, "_lsp_service"):
        self._lsp_service = LSPService(self.workspace)
    return self._lsp_service


def create_provider_agent(self, max_iterations=3):
    from .provider_agent import ProviderAgentRuntime
    return ProviderAgentRuntime(
        self,
        changes=self.changes,
        verification=self.verification,
        max_iterations=max_iterations,
    )

AgentRuntime.create_provider_agent = create_provider_agent

def transition(self, run_id, state, **detail):
    from .agent_runtime import RuntimeState
    state = RuntimeState(state)
    self._runtime_states[run_id] = state
    run = self.runs.get(run_id)
    if run is not None:
        setattr(run, "runtime_state", state)
        events = getattr(run, "events", None)
        if isinstance(events, list):
            events.append({"type": "run.transition", "state": state.value, "detail": detail})
    return run

AgentRuntime.transition = transition

def record_decision(self, run_id, decision):
    run = self.runs.get(run_id)
    if run is not None:
        if not hasattr(run, "decisions"):
            run.decisions = []
        run.decisions.append(decision)
    return run

AgentRuntime.record_decision = record_decision

def create_action_planner(self):
    from .action_planning import RuntimeActionPlanner
    return RuntimeActionPlanner(self)

AgentRuntime.create_action_planner = create_action_planner

def create_action_resolver(self):
    from .action_resolution import RuntimeActionResolver
    return RuntimeActionResolver(self)

AgentRuntime.create_action_resolver = create_action_resolver

def create_execution_planner(self):
    from .execution_planning import RuntimeExecutionPlanner
    return RuntimeExecutionPlanner(self)

AgentRuntime.create_execution_planner = create_execution_planner

def create_tool_executor(self):
    from .tool_execution import RuntimeToolExecutor
    return RuntimeToolExecutor(self)

AgentRuntime.create_tool_executor = create_tool_executor

def create_execution_control(self):
    if self._execution_control is None:
        from .execution_control import RuntimeExecutionControl
        self._execution_control = RuntimeExecutionControl(self)
    return self._execution_control

AgentRuntime.create_execution_control = create_execution_control

def create_persistence(self, database_url=None, redis_url=None):
    if self._persistence is None:
        from .persistence import RuntimePersistence
        self._persistence = RuntimePersistence(database_url=database_url, redis_url=redis_url, workspace=str(self.workspace))
    return self._persistence

AgentRuntime.create_persistence = create_persistence

def create_live_bridge(self):
    if self._live_bridge is None:
        from .live_bridge import RuntimeLiveBridge
        self._live_bridge = RuntimeLiveBridge(self)
    return self._live_bridge

AgentRuntime.create_live_bridge = create_live_bridge

def create_approval_center(self):
    if self._approval_center is None:
        from .approval import RuntimeApprovalCenter
        self._approval_center = RuntimeApprovalCenter(self)
    return self._approval_center

AgentRuntime.create_approval_center = create_approval_center

def create_execution_resumer(self):
    from .execution_resume import RuntimeExecutionResumer
    return RuntimeExecutionResumer(self)

AgentRuntime.create_execution_resumer = create_execution_resumer

def create_codix_learning(self):
    from .codix_learning import RuntimeCodixLearning
    return RuntimeCodixLearning(self)
AgentRuntime.create_codix_learning=create_codix_learning

def create_codix_training(self):
    from .codix_training import RuntimeCodixTraining
    return RuntimeCodixTraining(self)

AgentRuntime.create_codix_training = create_codix_training
