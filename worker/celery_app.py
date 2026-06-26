import os

from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

app = Celery("vitalrank", broker=broker_url, backend=broker_url)
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]

import worker.tasks.audit  # noqa: E402  # noqa: E402
