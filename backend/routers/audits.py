from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from backend import crud
from backend.auth import get_current_user
from backend.schemas import AuditCreate, AuditOut, AuditReport
from backend.tasks import enqueue_audit

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("", response_model=AuditOut, status_code=201)
def create_audit(
    data: AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Запускает аудит URL. Создаёт сайт автоматически, если его ещё нет."""
    site = crud.get_or_create_site(db, current_user, data.url)
    audit = crud.create_audit(db, site)
    enqueue_audit(audit.id)
    return audit


@router.get("/{audit_id}", response_model=AuditReport)
def get_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Статус и (когда готов) полный отчёт по аудиту."""
    audit = crud.get_audit(db, audit_id, current_user)
    if audit is None:
        raise HTTPException(status_code=404, detail="Аудит не найден")
    return audit
