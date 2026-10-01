from __future__ import annotations

from enum import IntEnum


class JobPriority(IntEnum):
    LOW = 10
    NORMAL = 50
    HIGH = 80
    CRITICAL = 100
