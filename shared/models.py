from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sites = relationship("Site", back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")


class Site(Base):
    """Постоянный сайт пользователя. Аудиты привязаны к нему."""
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String, nullable=False)          # основной URL для аудита
    domain = Column(String, nullable=True)        # домен для отображения
    cms = Column(String, nullable=True)           # определённая CMS: wordpress / bitrix / tilda / null
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="sites")
    audits = relationship("Audit", back_populates="site", cascade="all, delete-orphan")


class Audit(Base):
    """Один прогон аудита сайта. Снапшот состояния на момент проверки."""
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)

    # pending -> processing -> done / failed
    status = Column(String, default="pending", nullable=False)
    error = Column(Text, nullable=True)           # текст ошибки если failed

    # баллы 0-100, заполняются когда status = done
    google_score = Column(Integer, nullable=True)
    yandex_score = Column(Integer, nullable=True)
    health_score = Column(Integer, nullable=True)  # среднее двух
    score_delta = Column(Integer, nullable=True)   # разница с предыдущим аудитом (для флага регрессии)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    site = relationship("Site", back_populates="audits")
    results = relationship("AuditResult", back_populates="audit", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="audit", cascade="all, delete-orphan")


class AuditResult(Base):
    """Сырьё от одного модуля-коллектора как есть (JSONB)."""
    __tablename__ = "audit_results"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True)
    module = Column(String, nullable=False)       # tech_audit / pagespeed / link_checker
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    audit = relationship("Audit", back_populates="results")


class Issue(Base):
    """Факт найденной проблемы. Оценка под движки лежит в issue_scores."""
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_id = Column(String, nullable=False)      # ссылка на правило в каталоге
    page_url = Column(String, nullable=True)      # на какой странице нашли
    category = Column(String, nullable=True)      # meta / indexing / speed / links / trust / mobile
    title = Column(String, nullable=False)        # снапшот заголовка проблемы
    description = Column(Text, nullable=True)      # почему важно
    detail = Column(Text, nullable=True)          # конкретика ("Title 75 символов")
    code_snippet = Column(Text, nullable=True)    # готовый фикс под CMS сайта (уже резолвнутый)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    audit = relationship("Audit", back_populates="issues")
    scores = relationship("IssueScore", back_populates="issue", cascade="all, delete-orphan")


class IssueScore(Base):
    """Оценка одной проблемы под конкретный движок. 1-2 строки на проблему."""
    __tablename__ = "issue_scores"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)

    engine = Column(String, nullable=False)       # google / yandex
    effect = Column(Integer, nullable=False)      # вес правила под этот движок
    effort = Column(Integer, nullable=False)      # сложность фикса: 1=low, 2=med, 3=high
    priority_score = Column(Float, nullable=False)  # effect / effort
    bucket = Column(String, nullable=False)       # quick_win / long
    is_critical = Column(Boolean, default=False, nullable=False)

    issue = relationship("Issue", back_populates="scores")
