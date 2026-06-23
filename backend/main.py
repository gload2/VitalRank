from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.database import engine, Base
import shared.models  # noqa: F401  регистрирует таблицы на Base.metadata
from backend.config import FRONTEND_URL
from backend.routers.auth import router as auth_router
from backend.routers.audits import router as audits_router
from backend.routers.sites import router as sites_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # источник правды о схеме это модели, таблицы создаются при старте
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="VitalRank API", version="0.1.0", lifespan=lifespan)

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


@app.get("/ping")
def ping():
    return {"status": "ok"}
