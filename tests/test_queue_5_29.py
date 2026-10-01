from berkios.queue import Job, JobState
from berkios.queue.worker import JobWorker

def test_job_model():
    j = Job("demo", {"x": 1})
    assert j.state == JobState.QUEUED
    assert j.to_dict()["kind"] == "demo"

def test_worker_handler_without_persistence():
    class Q:
        def __init__(self): self.done = False
        def dequeue(self, timeout=1):
            if self.done: return None
            self.done = True
            return {"id":"1","kind":"demo","payload":{"x":2},"attempts":0}
    events=[]
    w=JobWorker(Q(), {"demo":lambda p:p["x"]+1}, lambda e,j:events.append(e))
    assert w.run_once()
    assert events == ["job.started", "job.completed"]
