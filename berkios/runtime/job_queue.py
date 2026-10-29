from __future__ import annotations

import uuid

from ..queue import Job, RedisJobQueue, JobWorker
from ..queue.worker import WorkerConfig, recover_expired_jobs
from ..persistence.repository import PersistenceRepository


class RuntimeJobQueue:
    """
    Façade durable PostgreSQL + Redis.

    Les handlers sont injectés par le runtime.
    """

    def __init__(
        self,
        redis_url=None,
        handlers=None,
        on_event=None,
        repository=None,
        lease_seconds=60,
    ):
        self.repository = (
            repository
            or PersistenceRepository()
        )

        self.queue = RedisJobQueue(
            redis_url
        )

        self.worker = JobWorker(
            self.queue,
            self.repository,
            handlers=handlers,
            config=WorkerConfig(
                lease_seconds=lease_seconds,
            ),
        )

        if on_event is not None:
            self.worker.event_callback = on_event

    def enqueue(
        self,
        kind,
        payload,
        max_attempts=3,
    ):
        job = Job(
            id=uuid.uuid4().hex,
            kind=kind,
            payload=payload,
            max_attempts=max_attempts,
        )

        self.repository.create_job(
            job.to_dict()
        )

        self.queue.enqueue(
            job
        )

        return job

    def run_once(self):
        return self.worker.run_once()

    def start(self):
        return self.worker.run_forever()

    def stop(self):
        return self.worker.stop()

    def recover(self):
        return recover_expired_jobs(
            self.repository,
            self.queue,
        )

    @property
    def available(self):
        return self.queue.available
