class PermissionManager:
    def __init__(self):
        self.allowed = {"project.read", "git.read"}
        self.session_grants = set()
    def grant(self, permission):
        self.session_grants.add(permission)
    def revoke(self, permission):
        self.session_grants.discard(permission)
    def is_allowed(self, permission):
        return permission in self.allowed or permission in self.session_grants
