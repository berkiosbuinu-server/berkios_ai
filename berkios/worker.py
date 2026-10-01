import os
from .runtime.job_queue import RuntimeJobQueue

def main():
    queue = RuntimeJobQueue(redis_url=os.getenv("BERKIOS_REDIS_URL"))
    print(f"Berkios durable worker started: {queue.worker.worker_id}", flush=True)
    queue.start()

if __name__ == "__main__": main()
