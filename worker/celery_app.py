import os

from celery import Celery

BROKER_URL = (
    os.getenv("CELERY_BROKER_URL")
    or os.getenv("REDIS_URL")
    or "redis://{host}:{port}/{db}".format(
        host=os.getenv("REDIS_HOST", "redis"),
        port=os.getenv("REDIS_PORT", "6379"),
        db=os.getenv("REDIS_DB", "0"),
    )
)

celery_app = Celery(
    "vitalrank_worker",
    broker=BROKER_URL,
    backend=BROKER_URL,
    include=["worker.tasks.audit"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=120,
    task_soft_time_limit=100,
    worker_prefetch_multiplier=1,
    result_expires=86400,
)

app = celery_app
