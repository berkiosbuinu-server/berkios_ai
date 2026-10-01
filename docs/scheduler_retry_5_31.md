# Berkios 5.31 — Scheduler + Retry Policy

Berkios 5.31 adds the scheduling and retry policy layer for the distributed
runtime.

## Capabilities

- delayed job scheduling;
- explicit priorities;
- configurable maximum attempts;
- exponential backoff;
- bounded jitter to avoid retry storms;
- scheduler kept separate from durable persistence.

## Important

The in-process scheduler is a dispatch layer, not a distributed scheduler.
For production HA, scheduled jobs should be persisted and claimed atomically
by the database before enqueueing.

Retries should only be used for operations that are safe to repeat or have
idempotency protection.
