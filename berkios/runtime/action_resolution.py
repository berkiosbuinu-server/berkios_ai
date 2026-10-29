
from __future__ import annotations

from berkios.actionplan import CapabilityResolver


class RuntimeActionResolver:
    """Adaptateur runtime vers le vrai ToolRegistry."""

    def __init__(self, runtime):
        self.runtime = runtime

        registry = getattr(runtime, "tools", None)
        permissions = getattr(registry, "permissions", None)

        self.resolver = CapabilityResolver(
            registry=registry,
            permissions=permissions,
        )

    def resolve(self, plan):
        return self.resolver.resolve(plan)

    def as_dict(self, plan):
        return self.resolver.to_dict(self.resolve(plan))
