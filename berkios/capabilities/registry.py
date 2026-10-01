class CapabilityRegistry:
    def __init__(self):
        self.items = {}
    def register(self, capability_id, handler, description=""):
        self.items[capability_id] = {"id": capability_id, "description": description, "handler": handler}
    def list(self):
        return [{k:v for k,v in x.items() if k != "handler"} for x in self.items.values()]
    def execute(self, capability_id, args=None):
        return self.items[capability_id]["handler"](**(args or {}))
