from berkios.changeintelligence import ChangeImpactPlanner

class RuntimeChangeImpact:
    def __init__(self,workspace):
        self.planner=ChangeImpactPlanner(workspace)
    def plan(self,target,change_description=""):
        return self.planner.plan(target,change_description).to_dict()
