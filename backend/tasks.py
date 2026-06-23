from celery import Celery

from backend.config import CELERY_BROKER_URL

# Лёгкий клиент Celery: бэк только ставит задачи в очередь.
# Саму задачу с этим именем реализует воркер (зона worker/).
celery_app = Celery("vitalrank", broker=CELERY_BROKER_URL)

WORKER_TASK_NAME = "worker.run_audit"


def enqueue_audit(audit_id: int) -> None:
    """Кладёт задачу аудита в очередь по имени, не импортируя код воркера."""
    celery_app.send_task(WORKER_TASK_NAME, args=[audit_id])
