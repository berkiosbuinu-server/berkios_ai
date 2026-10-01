from __future__ import annotations
import json, os
from .models import Job

class RedisJobQueue:
    def __init__(self, url=None, queue_name="berkios.jobs"):
        self.url = url or os.getenv("BERKIOS_REDIS_URL", "")
        self.queue_name = queue_name
        self.client = None
        if self.url:
            try:
                import redis
                self.client = redis.Redis.from_url(self.url, decode_responses=True)
                self.client.ping()
            except Exception:
                self.client = None
    @property
    def available(self): return self.client is not None
    def enqueue(self, job: Job | dict):
        if not self.client: raise RuntimeError("redis_unavailable")
        data = job.to_dict() if isinstance(job, Job) else job
        self.client.rpush(self.queue_name, json.dumps(data))
        return job
    def dequeue(self, timeout=5):
        if not self.client: return None
        item = self.client.blpop(self.queue_name, timeout=timeout)
        return json.loads(item[1]) if item else None
