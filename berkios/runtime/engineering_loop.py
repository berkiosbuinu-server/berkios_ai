from berkios.engineeringloop import EngineeringLoop

class RuntimeEngineeringLoop:
    def __init__(self,workspace,**components):
        self.loop=EngineeringLoop(workspace,**components)
    def start(self,target,request):
        return self.loop.start(target,request).to_dict()
    def approve(self,run):
        return self.loop.approve(run).to_dict()
    def verification(self,run,passed,message="",error_kind="unknown"):
        return self.loop.record_verification(run,passed,message,error_kind).to_dict()
