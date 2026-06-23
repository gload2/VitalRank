from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from shared.database import engine, Base
import shared.models  # noqa: F401  регистрирует таблицы на Base.metadata
from backend.config import FRONTEND_URL
from backend.routers.auth import router as auth_router
from backend.routers.audits import router as audits_router
from backend.routers.sites import router as sites_router
from backend.routers.demo import router as demo_router

DESCRIPTION = """
Сервис SEO-аудита сайта. Принимает URL, собирает технические данные,
скорость и Core Web Vitals, и выдаёт рекомендации двумя треками:
по логике Google и по логике Яндекса, отсортированные по эффект/усилие.
"""

tags_metadata = [
    {"name": "auth", "description": "Регистрация, вход, JWT-токены."},
    {"name": "audits", "description": "Запуск аудита и получение отчёта."},
    {"name": "sites", "description": "Сайты пользователя и история проверок."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # источник правды о схеме это модели, таблицы создаются при старте
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VitalRank API",
    description=DESCRIPTION,
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(audits_router)
app.include_router(sites_router)
app.include_router(demo_router)


@app.get("/", tags=["service"], summary="Информация о сервисе")
def root():
    return {"service": "VitalRank API", "version": "0.1.0", "docs": "/docs"}


@app.get("/ping", tags=["service"], summary="Проверка живости")
def ping():
    return {"status": "ok"}


@app.get("/health", tags=["service"], summary="Проверка БД")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except Exception as exc:
        return {"status": "degraded", "database": "down", "detail": str(exc)[:100]}
