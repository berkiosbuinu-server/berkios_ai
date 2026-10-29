
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CapabilityMatch:
    action_id: str
    capability: str | None
    tool: str | None
    available: bool
    requires_permission: bool = False
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class CapabilityResolver:
    """Résout les capacités d'un ActionPlan vers le ToolRegistry réel.

    Cette classe ne lance jamais un outil.
    Elle vérifie uniquement :
      - si la capacité existe ;
      - si une permission est nécessaire ;
      - les informations utiles à l'ExecutionPlanner.
    """

    def __init__(self, registry=None, permissions=None):
        self.registry = registry
        self.permissions = permissions or getattr(registry, "permissions", None)

    def _tool(self, capability: str | None):
        if not capability or self.registry is None:
            return None

        getter = getattr(self.registry, "get", None)
        if callable(getter):
            try:
                return getter(capability)
            except Exception:
                pass

        tools = getattr(self.registry, "tools", None)
        if isinstance(tools, dict):
            return tools.get(capability)

        return None

    def _available(self, capability: str | None) -> bool:
        return self._tool(capability) is not None

    def _permission(self, capability: str | None) -> str | None:
        tool = self._tool(capability)
        if tool is None:
            return None
        return getattr(tool, "permission", None)

    def _permission_allowed(self, capability: str | None) -> bool:
        permission = self._permission(capability)

        if not permission:
            return True

        permissions = self.permissions
        if permissions is None:
            return False

        checker = getattr(permissions, "is_allowed", None)
        if not callable(checker):
            return False

        try:
            return bool(checker(permission))
        except Exception:
            return False

    def resolve(self, plan):
        matches = []

        for action in plan.actions:
            capability = action.capability
            available = self._available(capability)
            permission = self._permission(capability)

            requires_permission = bool(
                available and permission and not self._permission_allowed(capability)
            )

            if not available:
                reason = "capacité non enregistrée"
            elif requires_permission:
                reason = f"permission requise: {permission}"
            elif action.requires_approval:
                reason = "capacité disponible; approbation séparée requise"
            else:
                reason = "capacité disponible"

            matches.append(
                CapabilityMatch(
                    action_id=action.id,
                    capability=capability,
                    tool=action.tool or capability,
                    available=available,
                    requires_permission=requires_permission,
                    reason=reason,
                    metadata={
                        "permission": permission,
                    },
                )
            )

        return matches

    def to_dict(self, matches):
        return [m.__dict__ for m in matches]
