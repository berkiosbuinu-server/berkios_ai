from berkios.learning.evaluation import CodixEvaluator, CodixModelRegistry
class RuntimeCodixEvaluation:
    def __init__(self, root=".berkios/model_registry"):
        self.evaluator=CodixEvaluator()
        self.registry=CodixModelRegistry(root)
