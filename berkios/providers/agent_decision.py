from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentDecision:
    action: str
    reason: str = ""
    proposal: dict[str, Any] = field(default_factory=dict)
    repair: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "action": self.action,
            "reason": self.reason,
            "proposal": self.proposal,
            "repair": self.repair,
            "metadata": self.metadata,
        }

class ProviderDecisionAdapter:
    """Normalizes different provider interfaces into AgentDecision."""

    def __init__(self, provider):
        self.provider = provider

    def decide(self, request: str, context: dict[str, Any]) -> AgentDecision:
        if self.provider is None:
            return AgentDecision(
                action="noop",
                reason="provider_unavailable",
            )

        raw = None
        for name in ("decide", "plan", "complete", "run"):
            method = getattr(self.provider, name, None)
            if callable(method):
                try:
                    raw = method(request, context)
                    break
                except TypeError:
                    try:
                        raw = method(request)
                        break
                    except Exception:
                        pass
                except Exception:
                    pass

        if isinstance(raw, AgentDecision):
            return raw

        if isinstance(raw, dict):
            return AgentDecision(
                action=raw.get("action", "noop"),
                reason=raw.get("reason", ""),
                proposal=raw.get("proposal", {}),
                repair=raw.get("repair", {}),
                metadata=raw.get("metadata", {}),
            )

        if isinstance(raw, str):
            return AgentDecision(
                action="message",
                reason=raw,
            )

        return AgentDecision(
            action="noop",
            reason="provider_returned_no_decision",
        )
