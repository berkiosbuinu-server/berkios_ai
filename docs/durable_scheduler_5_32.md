# Berkios 5.32 — Distributed Durable Scheduler

Berkios 5.32 moves scheduling from an in-memory-only mechanism toward a
PostgreSQL-backed distributed scheduler.

## Design

- PostgreSQL is the source of truth for schedules.
- Multiple scheduler processes can run concurrently.
- Due schedules are atomically claimed.
- Claimed schedules are converted into queue jobs.
- Successful dispatch advances the schedule.
- Dispatch failures release the claim for another attempt.
- Scheduler state survives process restarts.

## PostgreSQL implementation note

The production repository should claim due rows atomically using a transaction,
row locking, and `SKIP LOCKED` where appropriate. This prevents two scheduler
instances from dispatching the same occurrence concurrently.

This layer still does not promise exactly-once external side effects.
Idempotency remains required for jobs that can be retried.
