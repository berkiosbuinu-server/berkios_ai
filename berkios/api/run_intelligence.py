from berkios.agent.run_context import AgentRunContext

def prepare(workspace, request: str, runtime=None, run_memory=None,
            active_file=None, selection=None, target_nodes=None):
    context = AgentRunContext(workspace, runtime, run_memory)
    return context.prepare(
        request,
        active_file=active_file,
        selection=selection,
        target_nodes=target_nodes or [],
    ).to_dict()
