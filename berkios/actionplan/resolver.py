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
    """Résout les étapes d'un ActionPlan vers les capacités disponibles.

    Il ne lance aucun outil et ne transforme jamais une capacité en autorisation.
    """

    def __init__(self, registry=None, permissions=None):
        self.registry = registry
        self.permissions = permissions

    def _available(self, capability: str | None) -> bool:
        if not capability:
            return False
        if self.registry is None:
            return True
        try:
            return self.registry.get(capability) is not None
        except Exception:
            try:
                return any(
                    getattr(x, "id", None) == capability
                    for x in self.registry.list()
                )
            except Exception:
                return False

    def resolve(self, plan):
        matches = []
        for action in plan.actions:
            available = self._available(action.capability)
            protected = bool(action.requires_approval)
            matches.append(CapabilityMatch(
                action_id=action.id,
                capability=action.capability,
                tool=action.tool,
                available=available,
                requires_permission=protected,
                reason=(
                    "capacité disponible; autorisation séparée requise"
                    if available and protected
                    else "capacité disponible"
                    if available
                    else "capacité non enregistrée"
                ),
            ))
        return matches

    def to_dict(self, matches):
        return [m.__dict__ for m in matches]
