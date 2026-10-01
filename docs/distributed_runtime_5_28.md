# Berkios 5.28 — Distributed Job Runtime

5.28 adds a Redis-backed job queue and worker foundation.

## Flow
API/runtime -> Redis queue -> worker -> handler -> durable event/persistence.

Jobs have IDs, states, attempt counts, timestamps and errors.

## Important
This is a queue foundation, not yet a full distributed scheduler. A job is removed
from the Redis list when a worker claims it. Durable job-state persistence should be
added as the next hardening step so a worker crash can requeue an in-flight job.

The existing execution/approval permissions remain authoritative.
