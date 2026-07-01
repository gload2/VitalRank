from urllib.parse import urlparse

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from shared.models import User, Site, Audit, Issue
from backend.auth import hash_password, verify_password

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

def get_site_by_url(db: Session, user: User, url: str) -> Site | None:
    return db.query(Site).filter(Site.user_id == user.id, Site.url == url).first()


def count_sites(db: Session, user: User) -> int:
    return db.query(func.count(Site.id)).filter(Site.user_id == user.id).scalar() or 0


def get_or_create_site(db: Session, user: User, url: str) -> Site:
    site = get_site_by_url(db, user, url)
    if site:
        return site
    site = Site(user_id=user.id, url=url, domain=urlparse(url).netloc or None)
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def set_plan(db: Session, user: User, plan: str) -> User:
    user.plan = plan
    db.commit()
    db.refresh(user)
    return user


def update_profile(db: Session, user: User, name: str | None) -> User:
    user.name = name
    db.commit()
    db.refresh(user)
    return user


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
    sites = (
        db.query(Site)
        .filter(Site.user_id == user.id)
        .order_by(Site.created_at.desc())
        .all()
    )
    if not sites:
        return sites

    site_ids = [s.id for s in sites]
    latest_ids = [
        row[0]
        for row in db.query(func.max(Audit.id))
        .filter(Audit.site_id.in_(site_ids))
        .group_by(Audit.site_id)
        .all()
    ]
    by_site = {a.site_id: a for a in db.query(Audit).filter(Audit.id.in_(latest_ids)).all()}
    for site in sites:
        site.latest_audit = by_site.get(site.id)
    return sites


def get_site_detail(db: Session, site_id: int, user: User) -> Site | None:
    site = get_site(db, site_id, user)
    if site is None:
        return None
    site.latest_audit = _latest_audit(db, site.id)
    return site


def delete_site(db: Session, site_id: int, user: User) -> bool:
    site = get_site(db, site_id, user)
    if site is None:
        return False
    db.delete(site)
    db.commit()
    return True

def create_audit(db: Session, site: Site) -> Audit:
    audit = Audit(site_id=site.id, status="pending")
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


def get_audit(db: Session, audit_id: int, user: User) -> Audit | None:
    return (
        db.query(Audit)
        .join(Site, Audit.site_id == Site.id)
        .filter(Audit.id == audit_id, Site.user_id == user.id)
        .options(joinedload(Audit.issues).joinedload(Issue.scores))
        .first()
    )


def list_site_audits(
    db: Session, site_id: int, user: User, limit: int = 20, offset: int = 0
) -> list[Audit] | None:
    site = get_site(db, site_id, user)
    if site is None:
        return None
    return (
        db.query(Audit)
        .filter(Audit.site_id == site_id)
        .order_by(Audit.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


def delete_audit(db: Session, audit_id: int, user: User) -> bool:
    audit = get_audit(db, audit_id, user)
    if audit is None:
        return False
    db.delete(audit)
    db.commit()
    return True
