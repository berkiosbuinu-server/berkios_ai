from __future__ import annotations

import os

from .queue.job_handlers import build_job_handlers
from .runtime.app import create_runtime
from .runtime.job_queue import RuntimeJobQueue


def main() -> None:
    runtime = create_runtime()

    handlers = build_job_handlers(runtime)

    queue = RuntimeJobQueue(
        redis_url=os.getenv("BERKIOS_REDIS_URL"),
        handlers=handlers,
        repository=runtime.create_persistence().repository,
    )

    print(
        "Berkios durable worker started: "
        f"{queue.worker.worker_id}",
        flush=True,
    )

    print(
        "Registered job handlers: "
        + ", ".join(sorted(handlers)),
        flush=True,
    )

    queue.start()


if __name__ == "__main__":
    main()
