from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 2.0
    max_delay_seconds: float = 300.0
    jitter: float = 0.20

    def delay_for(self, attempt: int) -> float:
        """Exponential backoff with bounded positive jitter."""
        if attempt < 1:
            attempt = 1
        raw = min(
            self.max_delay_seconds,
            self.base_delay_seconds * (2 ** (attempt - 1)),
        )
        spread = raw * max(0.0, self.jitter)
        return max(0.0, raw + random.uniform(-spread, spread))
