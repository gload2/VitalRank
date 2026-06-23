from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from shared.url_guard import is_safe_public_url
from backend import crud
from backend.auth import get_current_user
from backend.schemas import (
    AuditCreate,
    AuditOut,
    AuditReport,
    CompareOut,
    CategoryCompare,
)
from backend.tasks import enqueue_audit
from backend.pdf_report import build_pdf

router = APIRouter(prefix="/audits", tags=["audits"])


@router.post("", response_model=AuditOut, status_code=201, summary="Запустить аудит URL")
def create_audit(
    data: AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Запускает аудит URL. Создаёт сайт автоматически, если его ещё нет."""
    ok, reason = is_safe_public_url(data.url)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Недопустимый URL: {reason}")

    site = crud.get_or_create_site(db, current_user, data.url)
    audit = crud.create_audit(db, site)

    try:
        enqueue_audit(audit.id)
    except Exception:
        audit.status = "failed"
        audit.error = "Не удалось поставить задачу в очередь"
        db.commit()
        raise HTTPException(status_code=503, detail="Сервис аудита временно недоступен")

    return audit


@router.get("/compare", response_model=CompareOut, summary="Сравнить два аудита")
def compare_audits(
    a: int = Query(..., description="ID первого аудита"),
    b: int = Query(..., description="ID второго аудита (конкурент)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Сравнивает два готовых аудита по баллам и проблемам по категориям."""
    audit_a = crud.get_audit(db, a, current_user)
    audit_b = crud.get_audit(db, b, current_user)
    if audit_a is None or audit_b is None:
        raise HTTPException(status_code=404, detail="Аудит не найден")
    if audit_a.status != "done" or audit_b.status != "done":
        raise HTTPException(status_code=409, detail="Оба аудита должны быть завершены")

    cat_a = Counter(i.category for i in audit_a.issues)
    cat_b = Counter(i.category for i in audit_b.issues)
    categories = [
        CategoryCompare(category=cat, a_count=cat_a.get(cat, 0), b_count=cat_b.get(cat, 0))
        for cat in sorted(set(cat_a) | set(cat_b))
    ]

    return CompareOut(
        a=audit_a,
        b=audit_b,
        a_url=audit_a.site.url,
        b_url=audit_b.site.url,
        google_diff=(audit_a.google_score or 0) - (audit_b.google_score or 0),
        yandex_diff=(audit_a.yandex_score or 0) - (audit_b.yandex_score or 0),
        health_diff=(audit_a.health_score or 0) - (audit_b.health_score or 0),
        categories=categories,
    )


@router.get("/{audit_id}", response_model=AuditReport, summary="Статус и отчёт аудита")
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


@router.get("/{audit_id}/pdf", summary="Скачать отчёт в PDF")
def audit_pdf(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отдаёт готовый отчёт аудита в виде PDF-файла."""
    audit = crud.get_audit(db, audit_id, current_user)
    if audit is None:
        raise HTTPException(status_code=404, detail="Аудит не найден")
    if audit.status != "done":
        raise HTTPException(status_code=409, detail="Отчёт ещё не готов")
    pdf = build_pdf(audit)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="audit_{audit_id}.pdf"'},
    )


@router.delete("/{audit_id}", summary="Удалить аудит")
def delete_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаляет аудит со всеми его результатами и проблемами."""
    if not crud.delete_audit(db, audit_id, current_user):
        raise HTTPException(status_code=404, detail="Аудит не найден")
    return {"message": "Аудит удалён"}
