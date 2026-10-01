from berkios.graph.intelligence import ProjectGraphIntelligence

class GraphContextComposer:
    def __init__(self, workspace):
        self.intelligence = ProjectGraphIntelligence(workspace)

    def compose(self, node_id: str, depth: int = 2):
        return self.intelligence.context_for(node_id, depth)
