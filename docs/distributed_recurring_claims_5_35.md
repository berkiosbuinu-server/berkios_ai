# Berkios 5.35 — Distributed Recurring Job Claims

5.35 hardens recurring dispatch for multiple scheduler instances.

## Core guarantee

A due recurring occurrence must first be claimed atomically in PostgreSQL.
Only the process holding that claim may publish the occurrence to Redis.

Each occurrence receives a stable idempotency key:

`recurring:<schedule_id>:<scheduled_for>`

## Multi-scheduler flow

1. Scheduler A and B ask PostgreSQL for due occurrences.
2. PostgreSQL atomically claims each occurrence.
3. Only one scheduler receives a given occurrence.
4. The scheduler publishes a normal queue job.
5. Successful publication finalizes the occurrence and calculates the next run.
6. Publication failure releases the claim for recovery.

## Important delivery semantics

This prevents duplicate claims between healthy scheduler instances, but it
does not create exactly-once side effects across PostgreSQL and Redis.
The idempotency key must therefore be honored by consumers or by a future
outbox/inbox layer.
