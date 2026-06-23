FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir --timeout 120 --retries 10 -r backend/requirements.txt

COPY backend backend
COPY shared shared

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
