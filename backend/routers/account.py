from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from backend import crud
from backend import ai_fix as ai_fix_mod
from backend.auth import get_current_user
from backend.plans import PLANS, FEATURE_LABELS, get_plan, plan_allows
from backend.schemas import UserOut, PlanUpdate, ProfileUpdate, AiFixRequest, AiFixOut

router = APIRouter(prefix="/account", tags=["account"])


@router.get("/plans", summary="Список тарифов и их возможностей")
def list_plans():
    return {
        "plans": list(PLANS.values()),
        "feature_labels": FEATURE_LABELS,
    }


@router.get("/me", response_model=UserOut, summary="Текущий пользователь")
def account_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/plan", response_model=UserOut, summary="Сменить тариф (без оплаты)")
def change_plan(
    data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.set_plan(db, current_user, data.plan)


@router.patch("/profile", response_model=UserOut, summary="Обновить профиль (имя)")
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.update_profile(db, current_user, data.name)


@router.post("/ai-fix", response_model=AiFixOut, summary="AI-починка проблемы (тариф Business)")
async def generate_ai_fix(
    data: AiFixRequest,
    current_user: User = Depends(get_current_user),
):
    if not plan_allows(current_user.plan, "ai_fix"):
        raise HTTPException(status_code=403, detail="AI-починка доступна на тарифе Business")
    try:
        fix, used_page = await ai_fix_mod.generate_fix(
            title=data.title,
            description=data.description,
            page_url=data.page_url,
            code_snippet=data.code_snippet,
        )
    except ai_fix_mod.LLMUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI-сервис недоступен. Запустите Ollama и модель {ai_fix_mod.LLM_MODEL} ({exc}).",
        )
    return AiFixOut(fix=fix, model=ai_fix_mod.LLM_MODEL, used_page=used_page)
