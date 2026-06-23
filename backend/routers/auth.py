from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User
from backend import crud
from backend.auth import (
    issue_tokens,
    rotate_refresh_token,
    revoke_refresh_token,
    get_current_user,
)
from backend.schemas import UserCreate, UserOut, Token, RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    return crud.create_user(db, data.email, data.password)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # username в форме OAuth2 это наш email
    user = crud.authenticate_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return issue_tokens(db, user)


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return rotate_refresh_token(db, data.refresh_token)


@router.post("/logout")
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    revoke_refresh_token(db, data.refresh_token)
    return {"message": "Вы вышли из системы"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
