FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt worker/requirements.txt
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r worker/requirements.txt

COPY worker worker
COPY shared shared

ENV PYTHONPATH=/app

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
