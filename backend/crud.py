from urllib.parse import urlparse

from sqlalchemy.orm import Session, joinedload

from shared.models import User, Site, Audit, Issue
from backend.auth import hash_password, verify_password


# Пользователи

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


# Сайты

def get_or_create_site(db: Session, user: User, url: str) -> Site:
    """Находит сайт пользователя по URL или создаёт новый."""
    site = db.query(Site).filter(Site.user_id == user.id, Site.url == url).first()
    if site:
        return site
    site = Site(user_id=user.id, url=url, domain=urlparse(url).netloc or None)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def get_site(db: Session, site_id: int, user: User) -> Site | None:
    return (
        db.query(Site)
        .filter(Site.id == site_id, Site.user_id == user.id)
        .first()
    )


def _latest_audit(db: Session, site_id: int) -> Audit | None:
    return (
        db.query(Audit)
        .filter(Audit.site_id == site_id)
        .order_by(Audit.created_at.desc())
        .first()
    )


def list_sites(db: Session, user: User) -> list[Site]:
    """Сайты пользователя с прикреплённым последним аудитом (для дашборда)."""
    sites = (
        db.query(Site)
        .filter(Site.user_id == user.id)
        .order_by(Site.created_at.desc())
        .all()
    )
    for site in sites:
        # транзиентный атрибут, читается pydantic-схемой SiteOut
        site.latest_audit = _latest_audit(db, site.id)
    return sites


# Аудиты

def create_audit(db: Session, site: Site) -> Audit:
    audit = Audit(site_id=site.id, status="pending")
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_audit(db: Session, audit_id: int, user: User) -> Audit | None:
    """Аудит с проблемами и оценками, с проверкой принадлежности пользователю."""
    return (
        db.query(Audit)
        .join(Site, Audit.site_id == Site.id)
        .filter(Audit.id == audit_id, Site.user_id == user.id)
        .options(joinedload(Audit.issues).joinedload(Issue.scores))
        .first()
    )


def list_site_audits(db: Session, site_id: int, user: User) -> list[Audit] | None:
    """История аудитов сайта. None если сайт не принадлежит пользователю."""
    site = get_site(db, site_id, user)
    if site is None:
        return None
    return (
        db.query(Audit)
        .filter(Audit.site_id == site_id)
        .order_by(Audit.created_at.desc())
        .all()
    )
