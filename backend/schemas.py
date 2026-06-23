from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


# Auth

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_len(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Пароль должен быть не короче 6 символов")
        return v


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# Issues / scores

class IssueScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    engine: Literal["google", "yandex"]
    effect: int
    effort: int
    priority_score: float
    bucket: Literal["quick_win", "long"]
    is_critical: bool


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rule_id: str
    page_url: Optional[str] = None
    category: Optional[str] = None
    title: str
    description: Optional[str] = None
    detail: Optional[str] = None
    code_snippet: Optional[str] = None
    scores: List[IssueScoreOut] = []


# Audits

class AuditCreate(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL должен начинаться с http:// или https://")
        return v


class AuditOut(BaseModel):
    """Короткая карточка аудита: статус и баллы. Без списка проблем."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    site_id: int
    status: Literal["pending", "processing", "done", "failed"]
    google_score: Optional[int] = None
    yandex_score: Optional[int] = None
    health_score: Optional[int] = None
    score_delta: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None


class AuditReport(AuditOut):
    """Полный отчёт: карточка + все найденные проблемы с оценками."""
    issues: List[IssueOut] = []


# Sites

class SiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: str
    domain: Optional[str] = None
    cms: Optional[str] = None
    created_at: datetime
    latest_audit: Optional[AuditOut] = None
