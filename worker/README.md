# VitalRank Worker

Минимальная рабочая версия. Сейчас умеет: технический аудит страницы через Celery-задачу.

Проверки tech_audit:
- title — наличие и непустой тег title
- description — наличие meta description
- h1 — ровно один заголовок h1
- canonical — указана canonical-ссылка
- https — сайт работает по HTTPS
- images_alt — у всех изображений есть alt-атрибут
- robots — доступен robots.txt
- sitemap — доступен sitemap.xml

В разработке (до начала июля): PageSpeed / Core Web Vitals, проверка битых ссылок, раздельные анализаторы под Google и Яндекс, приоритизация рекомендаций.

## Запуск

```bash
pip install -r requirements.txt

# нужен запущенный Redis (брокер очереди)
redis-server

# запуск воркера
REDIS_HOST=localhost celery -A worker.celery_app worker --loglevel=info
```

## Стык с backend

Backend ставит задачу в очередь по имени `audit.run` и получает результат по task_id:

```python
from worker.tasks.audit import run_audit

result = run_audit.delay("https://example.com")
data = result.get(timeout=25)
```

Формат ответа:

```json
{
  "url": "https://example.com",
  "score": 88,
  "checks": [
    {"name": "title", "ok": true, "value": "..."},
    {"name": "robots", "ok": true, "value": "..."},
    {"name": "sitemap", "ok": false, "message": "..."}
  ]
}
```

`score` — процент пройденных проверок. Каждая проверка возвращает `value` при успехе или `message` при провале. Проверки robots и sitemap делают отдельные запросы к сайту; при сбое запроса проверка не роняет аудит, а возвращает сообщение об ошибке.
