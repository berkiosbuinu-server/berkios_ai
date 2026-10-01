from ..queue import Job, RedisJobQueue, JobWorker
from ..persistence.repository import PersistenceRepository

class RuntimeJobQueue:
    def __init__(self, redis_url=None, handlers=None, on_event=None, repository=None, lease_seconds=60):
        self.repository = repository or PersistenceRepository()
        self.queue = RedisJobQueue(redis_url)
        self.worker = JobWorker(self.queue, handlers=handlers, on_event=on_event,
                                repository=self.repository, lease_seconds=lease_seconds)
    def enqueue(self, kind, payload, max_attempts=3):
        job = Job(kind=kind, payload=payload, max_attempts=max_attempts)
        self.repository.create_job(job.to_dict())
        self.queue.enqueue(job)
        return job
    def run_once(self): return self.worker.run_once()
    def start(self): return self.worker.run_forever()
    def stop(self): return self.worker.stop()
    def recover(self): return self.worker.recover()
    @property
    def available(self): return self.queue.available

def enqueue_job(job_queue, kind, payload, max_attempts=3):
    return job_queue.enqueue(kind, payload, max_attempts=max_attempts).to_dict()
