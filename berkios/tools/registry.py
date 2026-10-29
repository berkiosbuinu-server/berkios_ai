from __future__ import annotations


class ToolRegistry:
    """
    Registre unique des outils du runtime.

    Le registre est la source de vérité pour :
    - découvrir un outil ;
    - vérifier sa permission ;
    - exécuter l'outil.
    """

    def __init__(self, permissions):
        self.permissions = permissions
        self.tools = {}

    def register(self, tool):
        self.tools[tool.name] = tool

    def get(self, name):
        return self.tools.get(name)

    def has(self, name):
        return name in self.tools

    def can_execute(self, name):
        tool = self.get(name)

        if tool is None:
            return False

        permission = getattr(tool, "permission", None)

        if not permission:
            return True

        return bool(self.permissions.is_allowed(permission))

    def execute(self, name, args=None):
        args = args or {}

        tool = self.get(name)

        if tool is None:
            raise KeyError(f"Outil non enregistré: {name}")

        if not self.can_execute(name):
            permission = getattr(tool, "permission", None)
            raise PermissionError(
                f"Permission refusée pour {name}: {permission}"
            )

        return tool.execute(**args)

    def list(self):
        return list(self.tools)

    def items(self):
        return self.tools.items()
