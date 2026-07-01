from celery import Celery

from backend.config import CELERY_BROKER_URL

celery_app = Celery("vitalrank", broker=CELERY_BROKER_URL)

WORKER_TASK_NAME = "audit.run"


def enqueue_audit(audit_id: int) -> None:
    celery_app.send_task(WORKER_TASK_NAME, args=[audit_id])
