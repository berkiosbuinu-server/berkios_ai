from __future__ import annotations

import os

from berkios.persistence import Database, PersistenceRepository
from berkios.persistence.redis_bus import RedisEventBus

class RuntimePersistence:
    """Durable state facade used by Berkios runtimes.

    Existing in-memory managers can adopt this facade incrementally.
    """

    def __init__(self, database_url: str | None = None, redis_url: str | None = None, workspace=None):
        self.workspace = workspace
        self.database = Database(database_url or os.getenv("BERKIOS_DATABASE_URL"))
        self.repository = PersistenceRepository(self.database)
        self.events = RedisEventBus(redis_url or os.getenv("BERKIOS_REDIS_URL"))

    def record_run(self, run_id: str, state: str, payload: dict, project: str | None = None):
        self.repository.upsert_run(run_id, state, payload, project)
        self.events.publish("run.updated", {
            "run_id": run_id,
            "state": state,
            "project": project,
        })

    def record_event(self, event_type: str, payload: dict, run_id: str | None = None):
        event_id = self.repository.add_event(event_type, payload, run_id)
        self.events.publish(event_type, {
            "event_id": event_id,
            "run_id": run_id,
            **payload,
        })
        return event_id
