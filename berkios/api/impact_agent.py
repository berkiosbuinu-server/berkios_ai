from berkios.agent.impact import ImpactAwarePlanner

def analyze(workspace, request: str, targets: list[str]):
    return ImpactAwarePlanner(workspace).analyze_targets(targets, request).to_dict()
