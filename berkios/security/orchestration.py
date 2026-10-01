class PermissionGate:
    def __init__(self, manager=None):
        self.manager = manager

    def check(self, action: str, scope: str):
        if self.manager is None:
            return False
        for name in ("check", "allowed", "is_allowed"):
            method = getattr(self.manager, name, None)
            if callable(method):
                try:
                    return bool(method(action, scope))
                except TypeError:
                    try:
                        return bool(method(action))
                    except Exception:
                        pass
                except Exception:
                    pass
        return False
