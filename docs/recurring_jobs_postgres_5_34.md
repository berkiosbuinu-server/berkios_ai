# Berkios 5.34 — PostgreSQL Recurring Jobs

Recurring jobs are now represented by a persistent PostgreSQL table:
`berkios_recurring_jobs`.

## Lifecycle

1. A recurring definition is created with a cron expression.
2. Its `next_run_at` is persisted.
3. The dispatcher reads enabled definitions.
4. When due, it creates a normal durable queue `Job`.
5. The occurrence is recorded through `last_run_at`.
6. The next occurrence is calculated and persisted.

Activation/deactivation changes the `enabled` field without deleting the
recurring definition.

## Production concurrency

For multiple dispatcher instances, the read/claim/update sequence should be
wrapped in an atomic PostgreSQL transaction with row locking (for example
`FOR UPDATE SKIP LOCKED`) before enqueueing. The queue job should also carry
an idempotency key derived from the recurring job id and scheduled occurrence.

The implementation intentionally does not claim exactly-once external side
effects.
