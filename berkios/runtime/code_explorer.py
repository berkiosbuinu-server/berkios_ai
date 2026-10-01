from berkios.codeexplorer import CodeExplorer

class RuntimeCodeExplorer:
    def __init__(self,workspace):
        self.engine=CodeExplorer(workspace)

    def explore_symbol(self,path,symbol):
        return self.engine.explore_symbol(path,symbol).to_dict()

    def explore_file(self,path):
        return self.engine.explore_file(path).to_dict()
