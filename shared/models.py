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
    name = Column(String, nullable=True)
    plan = Column(String, default="free", nullable=False)
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
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String, nullable=False)
    domain = Column(String, nullable=True)
    cms = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="sites")
    audits = relationship("Audit", back_populates="site", cascade="all, delete-orphan")


class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String, default="pending", nullable=False)
    error = Column(Text, nullable=True)

    google_score = Column(Integer, nullable=True)
    yandex_score = Column(Integer, nullable=True)
    health_score = Column(Integer, nullable=True)
    score_delta = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    site = relationship("Site", back_populates="audits")
    results = relationship("AuditResult", back_populates="audit", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="audit", cascade="all, delete-orphan")


class AuditResult(Base):
    __tablename__ = "audit_results"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True)
    module = Column(String, nullable=False)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    audit = relationship("Audit", back_populates="results")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, index=True)

    rule_id = Column(String, nullable=False)
    page_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    detail = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    audit = relationship("Audit", back_populates="issues")
    scores = relationship("IssueScore", back_populates="issue", cascade="all, delete-orphan")


class IssueScore(Base):
    __tablename__ = "issue_scores"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True)

    engine = Column(String, nullable=False)
    effect = Column(Integer, nullable=False)
    effort = Column(Integer, nullable=False)
    priority_score = Column(Float, nullable=False)
    bucket = Column(String, nullable=False)
    is_critical = Column(Boolean, default=False, nullable=False)

    issue = relationship("Issue", back_populates="scores")
