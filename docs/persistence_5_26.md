# Berkios 5.26 — Durable Runtime Foundation

5.26 adds the first real persistence layer for Berkios.

## PostgreSQL

Tables:
- `berkios_runs`
- `berkios_approvals`
- `berkios_events`

The repository supports run upserts, approval persistence and cursor-based event reads.

## Redis

`RedisEventBus` publishes structured runtime events to `berkios.events`.
If Redis is unavailable, the persistent PostgreSQL event record remains the source of truth.

## Runtime

`RuntimePersistence` is deliberately a facade. Existing in-memory managers are not silently replaced.
They can adopt `record_run()` and `record_event()` incrementally.

## Local development

Without environment variables, the persistence layer defaults to SQLite:
`sqlite:///./.berkios.db`

Production Docker Compose uses PostgreSQL and Redis.

## Boundary

This release does not yet claim full migration of every historical in-memory manager.
The next step is to make execution runs, approvals and live event cursors use this durable store by default.
