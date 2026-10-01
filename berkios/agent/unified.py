from berkios.intelligence.unified import UnifiedIntelligence

class UnifiedAgentPreparation:
    def __init__(self, workspace, runtime=None):
        self.intelligence = UnifiedIntelligence(workspace, runtime)

    def prepare(self, request: str, active_file=None,
                selection=None, target_nodes=None):
        snapshot = self.intelligence.build(
            request=request,
            active_file=active_file,
            selection=selection,
            target_nodes=target_nodes or [],
        )
        return {
            "snapshot": snapshot.to_dict(),
            "planning_guidance": [
                "use project structure before editing",
                "consider active-file diagnostics",
                "consult relevant project memory",
                "review previous corrections when applicable",
                "inspect Git state before risky changes",
                "verify the affected scope after applying changes",
            ],
        }
