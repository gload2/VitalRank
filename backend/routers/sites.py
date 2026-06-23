from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from backend import crud
from backend.auth import get_current_user
from backend.schemas import SiteOut, AuditOut

router = APIRouter(prefix="/sites", tags=["sites"])


@router.get("", response_model=List[SiteOut], summary="Список сайтов пользователя")
def list_sites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Сайты пользователя с последним аудитом (для дашборда)."""
    return crud.list_sites(db, current_user)


@router.get("/{site_id}", response_model=SiteOut, summary="Один сайт")
def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    site = crud.get_site_detail(db, site_id, current_user)
    if site is None:
        raise HTTPException(status_code=404, detail="Сайт не найден")
    return site


@router.get("/{site_id}/audits", response_model=List[AuditOut], summary="История проверок сайта")
def site_audits(
    site_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """История аудитов конкретного сайта с пагинацией."""
    audits = crud.list_site_audits(db, site_id, current_user, limit=limit, offset=offset)
    if audits is None:
        raise HTTPException(status_code=404, detail="Сайт не найден")
    return audits


@router.delete("/{site_id}", summary="Удалить сайт")
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаляет сайт пользователя со всеми его аудитами."""
    if not crud.delete_site(db, site_id, current_user):
        raise HTTPException(status_code=404, detail="Сайт не найден")
    return {"message": "Сайт удалён"}
