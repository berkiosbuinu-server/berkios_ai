from __future__ import annotations
from berkios.actionplan import CapabilityResolver


class RuntimeActionResolver:
    def __init__(self, runtime):
        self.runtime = runtime
        self.resolver = CapabilityResolver(
            getattr(runtime, "capabilities", None),
            getattr(runtime, "permissions", None),
        )

    def resolve(self, plan):
        return self.resolver.resolve(plan)

    def as_dict(self, plan):
        return self.resolver.to_dict(self.resolve(plan))
