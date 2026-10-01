# Berkios 5.30 — Worker Heartbeat

Berkios 5.30 hardens the distributed job runtime with renewable worker leases.

## Runtime model

1. A worker claims a queued job.
2. The persistence layer records `worker_id` and a lease expiration.
3. A heartbeat thread renews the lease while the handler runs.
4. Completion/failure clears the lease.
5. If a worker disappears, a recovery pass can atomically requeue the expired job.
6. Another worker can then claim it.

## Production requirement

The persistence implementation must make `claim_job`, `heartbeat_job`,
`complete_job`, `fail_job`, and `requeue_expired_jobs` atomic transactions.
For long-running handlers, `heartbeat_seconds` should be comfortably below
`lease_seconds` (for example 20s / 60s).

This version is a runtime hardening layer; it does not claim exactly-once
execution for external side effects.
