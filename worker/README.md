# VitalRank Worker

Минимальная рабочая версия. Сейчас умеет: технический аудит страницы по трём проверкам (title, meta description, h1) через Celery-задачу.

В разработке (до начала июля): PageSpeed / Core Web Vitals, проверка битых ссылок, robots.txt и sitemap.xml, раздельные анализаторы под Google и Яндекс, приоритизация рекомендаций.

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
data = result.get(timeout=20)
```

Формат ответа:

```json
{
  "url": "https://example.com",
  "score": 100,
  "checks": [
    {"name": "title", "ok": true, "value": "..."},
    {"name": "description", "ok": true, "value": "..."},
    {"name": "h1", "ok": true, "value": "..."}
  ]
}
```

`score` — процент пройденных проверок. По мере добавления новых проверок формат `checks` будет расширяться.
