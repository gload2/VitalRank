from worker.celery_app import app
from worker.modules import tech_audit


@app.task(name="audit.run")
def run_audit(url):
    return tech_audit.run(url)
