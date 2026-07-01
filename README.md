# VitalRank

SEO-аудит сайта: backend (FastAPI) + worker (Celery/ML-проверки) + frontend (React),
поверх PostgreSQL и Redis.

## Как это связано

```
frontend (React)  ──HTTP /api──►  backend (FastAPI)  ──ставит задачу──►  Redis
        ▲                              │                                    │
        │ опрашивает статус            │ пишет/читает                       │ берёт задачу
        └──────────────────────────►  PostgreSQL  ◄────пишет результат──── worker (Celery)
```

1. Фронт логинится (`/api/auth/login`), создаёт аудит (`POST /api/audits`).
2. Backend создаёт строку `Audit` в статусе `pending` и кладёт задачу `audit.run` в Redis.
3. Worker берёт `audit_id`, прогоняет проверки, считает баллы и пишет проблемы в БД,
   ставит статус `done`.
4. Фронт опрашивает `GET /api/audits/{id}` (поллинг каждые 3 c) и показывает отчёт.

---

## Вариант A — всё в Docker (одной командой)

```bash
docker compose up --build
```

Поднимутся: postgres, redis, backend, worker, frontend.

- Фронтенд:  http://localhost:3000
- API/доки:  http://localhost:8000/docs

Фронт ходит на backend через nginx по тому же origin (`/api` → backend),
поэтому никакой доп. настройки не нужно.

Остановить: `docker compose down` (данные БД сохранятся в volume `pgdata`).

---

## Вариант B — локальная разработка

Инфраструктуру (БД + Redis) удобно держать в docker, а код запускать вручную:

```bash
docker compose up -d postgres redis
```

**Backend** (из корня репозитория):

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Worker** (из корня репозитория, отдельный терминал):

```bash
pip install -r worker/requirements.txt
celery -A worker.celery_app worker --loglevel=info        # на Windows можно добавить --pool=solo
```

**Frontend** (отдельный терминал):

```bash
npm install
npm start
```

Фронт поднимется на http://localhost:3000 и через `src/setupProxy.js` будет
проксировать `/api` → http://localhost:8000 (тот же путь, что в docker).

> Значения подключения берутся из `backend/.env` (см. `backend/.env.example`).
> Для прода обязательно поменяй `SECRET_KEY`.
