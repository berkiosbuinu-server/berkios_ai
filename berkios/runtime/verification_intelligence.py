from berkios.verificationintel import VerificationIntelligence

class RuntimeVerificationIntelligence:
    def __init__(self,workspace):
        self.engine=VerificationIntelligence(workspace)
    def inspect(self,change_target,targets):
        return self.engine.inspect_files(change_target,targets).to_dict()
    def python_check(self,target):
        return self.engine.run_python_check(target)
