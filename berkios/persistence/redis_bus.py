from __future__ import annotations

import json
import os

class RedisEventBus:
    def __init__(self, url: str | None = None, channel: str = "berkios.events"):
        self.url = url or os.getenv("BERKIOS_REDIS_URL", "")
        self.channel = channel
        self.client = None
        if self.url:
            try:
                import redis
                self.client = redis.Redis.from_url(self.url, decode_responses=True)
                self.client.ping()
            except Exception:
                self.client = None

    @property
    def available(self) -> bool:
        return self.client is not None

    def publish(self, event_type: str, payload: dict) -> bool:
        if not self.client:
            return False
        message = json.dumps({"event_type": event_type, "payload": payload}, ensure_ascii=False)
        self.client.publish(self.channel, message)
        return True
