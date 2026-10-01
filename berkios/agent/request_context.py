from berkios.agent.impact import ImpactAwarePlanner

class ImpactAwareRequestContext:
    def __init__(self, workspace):
        self.planner = ImpactAwarePlanner(workspace)

    def build(self, request: str, targets: list[str]):
        plan = self.planner.analyze_targets(targets, request)
        return {
            "request": request,
            "impact": plan.to_dict(),
            "instructions": [
                "consider affected files before editing",
                "review related symbols",
                "verify impacted areas after changes",
            ],
        }
