from __future__ import annotations

import calendar
import datetime as dt
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CronExpression:
    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"


class CronParseError(ValueError):
    pass


class CronEngine:
    """Small dependency-free cron engine.

    Supports *, comma lists, ranges, and */N steps for the standard
    five-field cron format: minute hour day-of-month month day-of-week.
    """

    LIMITS = (
        (0, 59),
        (0, 23),
        (1, 31),
        (1, 12),
        (0, 6),
    )

    def parse(self, expression: str) -> CronExpression:
        parts = expression.split()
        if len(parts) != 5:
            raise CronParseError("Cron expression must contain 5 fields")
        for value, (lo, hi) in zip(parts, self.LIMITS):
            self._validate_field(value, lo, hi)
        return CronExpression(*parts)

    def _validate_field(self, field: str, lo: int, hi: int) -> None:
        for token in field.split(","):
            base = token.split("/", 1)[0]
            if "/" in token:
                step = token.split("/", 1)[1]
                if not step.isdigit() or int(step) <= 0:
                    raise CronParseError(f"Invalid step: {token}")
            if base == "*":
                continue
            if "-" in base:
                a, b = base.split("-", 1)
                if not (a.isdigit() and b.isdigit()):
                    raise CronParseError(f"Invalid range: {token}")
                if not (lo <= int(a) <= int(b) <= hi):
                    raise CronParseError(f"Range out of bounds: {token}")
            elif not base.isdigit() or not (lo <= int(base) <= hi):
                raise CronParseError(f"Value out of bounds: {token}")

    def _values(self, field: str, lo: int, hi: int) -> set[int]:
        result: set[int] = set()
        for token in field.split(","):
            if "/" in token:
                base, step_s = token.split("/", 1)
                step = int(step_s)
            else:
                base, step = token, 1

            if base == "*":
                start, end = lo, hi
            elif "-" in base:
                a, b = base.split("-", 1)
                start, end = int(a), int(b)
            else:
                start = end = int(base)

            result.update(range(start, end + 1, step))
        return result

    def matches(self, expression: CronExpression, value: dt.datetime) -> bool:
        fields = [
            self._values(expression.minute, 0, 59),
            self._values(expression.hour, 0, 23),
            self._values(expression.day_of_month, 1, 31),
            self._values(expression.month, 1, 12),
            self._values(expression.day_of_week, 0, 6),
        ]
        # Python weekday is Monday=0; cron commonly uses Sunday=0.
        cron_dow = (value.weekday() + 1) % 7
        dom_ok = value.day in fields[2]
        dow_ok = cron_dow in fields[4]

        # Standard cron semantics: if both DOM and DOW are restricted,
        # either one may match.
        dom_restricted = expression.day_of_month != "*"
        dow_restricted = expression.day_of_week != "*"
        day_ok = (
            (dom_ok or dow_ok)
            if dom_restricted and dow_restricted
            else (dom_ok and dow_ok)
        )
        return (
            value.minute in fields[0]
            and value.hour in fields[1]
            and value.month in fields[3]
            and day_ok
        )

    def next_run(
        self,
        expression: CronExpression,
        after: dt.datetime,
        *,
        max_minutes: int = 366 * 24 * 60,
    ) -> dt.datetime:
        candidate = after.replace(second=0, microsecond=0) + dt.timedelta(minutes=1)
        for _ in range(max_minutes):
            if self.matches(expression, candidate):
                return candidate
            candidate += dt.timedelta(minutes=1)
        raise CronParseError("No matching time found within search horizon")
