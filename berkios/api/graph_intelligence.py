from berkios.graph.intelligence import ProjectGraphIntelligence

def impact(workspace, node_id: str, depth: int = 2):
    return ProjectGraphIntelligence(workspace).impact(node_id, depth).to_dict()

def context(workspace, node_id: str, depth: int = 2):
    return ProjectGraphIntelligence(workspace).context_for(node_id, depth)
