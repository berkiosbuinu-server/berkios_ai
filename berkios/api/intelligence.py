from berkios.intelligence.unified import UnifiedIntelligence

def snapshot(workspace, request: str, active_file=None,
             selection=None, target_nodes=None, runtime=None):
    return UnifiedIntelligence(workspace, runtime).build(
        request, active_file, selection, target_nodes or []
    ).to_dict()
