def enqueue_job(job_queue, kind, payload):
    job=job_queue.enqueue(kind,payload)
    return job.to_dict()
