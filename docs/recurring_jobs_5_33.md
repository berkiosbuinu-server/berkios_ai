# Berkios 5.33 — Cron / Recurring Jobs

Berkios 5.33 adds a dependency-free recurring-job engine.

## Supported cron syntax

Five fields:

`minute hour day-of-month month day-of-week`

Supported constructs:
- `*`
- comma lists: `1,15,30`
- ranges: `1-5`
- steps: `*/5`, `1-20/2`

Examples:
- `*/5 * * * *` — every 5 minutes
- `0 8 * * *` — every day at 08:00
- `0 9 * * 1-5` — weekdays at 09:00
- `30 2 1 * *` — first day of each month at 02:30

The recurring definition must be persisted. Each occurrence should become a
normal durable queue job, preserving the retry/lease guarantees of the runtime.

Timezone-aware scheduling should be implemented by the persistence/scheduler
layer using an explicit IANA timezone. The core parser itself is timezone
agnostic.
