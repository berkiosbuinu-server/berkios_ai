class ProviderEngine:
    def __init__(self):
        self.providers = {}
        self.selected = None
    def register(self, provider):
        self.providers[provider.name] = provider
        if self.selected is None:
            self.selected = provider.name
    def select(self, name):
        if name not in self.providers:
            raise KeyError(name)
        self.selected = name
    def current(self):
        return self.providers[self.selected]
    def list(self):
        return list(self.providers)
