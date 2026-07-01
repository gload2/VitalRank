# VitalRank Worker

Фоновый обработчик SEO-аудитов на Celery. Backend кладёт задачу в очередь по
`audit_id`, воркер сам собирает данные, считает баллы под Google и Яндекс и
пишет результат в общую БД.

## Что делает аудит

Три модуля сбора данных запускаются параллельно (`asyncio`):

- **tech_audit** — технический SEO: title (+длина), meta description (+длина),
  H1 (наличие/дубли), canonical, HTTPS, alt у изображений, robots.txt, sitemap.xml.
- **pagespeed** — Core Web Vitals (LCP / CLS / FID) через Google PageSpeed
  Insights API, отдельно для mobile и desktop. Ключ `PAGESPEED_API_KEY`
  необязателен (поднимает лимит запросов), см. `backend/.env.example`.
- **link_checker** — обход до 50 внутренних ссылок, поиск битых (4xx/5xx) и
  избыточных редиректов.

Падение одного модуля не роняет весь аудит — отчёт собирается из того, что удалось.

## Как считаются баллы

1. Модули отдают список проблем (`Issue`, единый формат — `worker/common/types.py`).
2. Два анализатора (`analyzers/google_analyzer.py`, `analyzers/yandex_analyzer.py`)
   взвешивают одни и те же проблемы **по-разному** (вес `effect` + трудозатраты `effort`).
3. `reports/report_generater.py` считает `health_score` 0-100 на каждый движок и
   раскладывает рекомендации на быстрые победы / долгое лечение по `effect/effort`.

## Стык с backend (контракт НЕ изменился)

Backend создаёт строку `Audit` в статусе `pending` и кладёт задачу:

```python
celery_app.send_task("audit.run", args=[audit_id])
```

Воркер (`worker/tasks/audit.py`) по `audit_id`:

1. загружает аудит и его сайт из общей БД (`shared/`);
2. переводит статус в `processing`;
3. прогоняет три модуля и собирает отчёт (два трека);
4. раскладывает отчёт в те же таблицы, что и раньше — `Issue` + `IssueScore`
   (по одной оценке на движок), сырой отчёт кладёт в `AuditResult(module="full_audit")`;
5. считает `google_score` / `yandex_score` / `health_score` (+ `score_delta` к прошлому);
6. ставит статус `done` (или `failed` с текстом ошибки при сбое).

Фронт и backend следят за прогрессом по полю `status` (`GET /audits/{id}`) —
формат `Issue`/`IssueScore` сохранён один-в-один, поэтому backend и frontend
работают без изменений.

## Запуск

```bash
pip install -r requirements.txt

# нужны запущенные Redis (брокер) и Postgres (воркер пишет результаты в общую БД):
#   docker compose up -d postgres redis

# запуск воркера (из КОРНЯ репозитория, чтобы виделись пакеты worker/ и shared/)
CELERY_BROKER_URL=redis://localhost:6379/0 \
DATABASE_URL=postgresql://vitalrank:vitalrank@localhost:5432/vitalrank \
celery -A worker.celery_app worker --loglevel=info
```

В Docker всё поднимается через корневой `docker-compose.yml` (сервис `worker`).
