from berkios.learning.continuous import CodixContinuousLearningLoop, LoopConfig
class RuntimeCodixContinuous:
    def __init__(self,root=".berkios/continuous_learning",config=None):
        self.loop=CodixContinuousLearningLoop(root,config)
    def run_once(self,**kwargs): return self.loop.run_once(**kwargs)
