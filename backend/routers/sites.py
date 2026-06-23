from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from backend import crud
from backend.auth import get_current_user
from backend.schemas import SiteOut, AuditOut

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=List[SiteOut])
def list_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Сайты пользователя с последним аудитом (для дашборда)."""
    return crud.list_sites(db, current_user)


@router.get("/{site_id}/audits", response_model=List[AuditOut])
def site_audits(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """История аудитов конкретного сайта."""
    audits = crud.list_site_audits(db, site_id, current_user)
    if audits is None:
        raise HTTPException(status_code=404, detail="Сайт не найден")
    return audits
