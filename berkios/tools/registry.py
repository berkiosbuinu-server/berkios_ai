class ToolRegistry:
    def __init__(self, permissions):
        self.permissions = permissions
        self.tools = {}
    def register(self, tool):
        self.tools[tool.name] = tool
    def can_execute(self, name):
        tool = self.tools[name]
        return self.permissions.is_allowed(tool.permission)
    def execute(self, name, args):
        if not self.can_execute(name):
            raise PermissionError(name)
        return self.tools[name].execute(**args)
    def list(self):
        return list(self.tools)
