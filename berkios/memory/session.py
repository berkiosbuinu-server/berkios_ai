class SessionMemory:
    def __init__(self):
        self.items = []
    def add(self, category, content):
        self.items.append({"category": category, "content": content})
    def list(self):
        return list(self.items)
