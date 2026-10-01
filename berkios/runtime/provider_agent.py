from __future__ import annotations
from typing import Any

from berkios.agent.loop2 import AgentLoop2


class ProviderAgentRuntime:
    """Connecte le provider sélectionné au cycle AgentLoop2.

    Le provider décide; le runtime garde l'autorité sur l'approbation,
    l'application et la vérification.
    """

    def __init__(self, runtime, changes=None, verification=None, lsp=None,
                 max_iterations=3):
        self.runtime = runtime
        self.changes = changes or runtime.changes
        self.verification = verification or runtime.verification
        self.lsp = lsp
        self.max_iterations = max_iterations

    def loop(self, request: str, run_id: str | None = None, **context):
        if run_id is None:
            # Le runtime principal possède déjà un registre de runs.
            loop = self.runtime.create_loop(request)
            run_id = loop.run_id

        provider = self.runtime.providers.current()
        agent = AgentLoop2(
            self.runtime,
            provider=provider,
            lsp=self.lsp,
            changes=self.changes,
            verification=self.verification,
            max_iterations=self.max_iterations,
        )
        return agent.run(run_id, request, **context)

    def provider_name(self) -> str:
        return self.runtime.providers.selected
