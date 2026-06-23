from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import User, RefreshToken
from backend.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не удалось проверить учётные данные",
    headers={"WWW-Authenticate": "Bearer"},
)


# пароли

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# токены

def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "type": "access", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(db: Session, user: User) -> str:
    """Создаёт refresh-токен и сохраняет его jti в БД (для возможности отзыва)."""
    jti = str(uuid4())
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expire))
    db.commit()
    payload = {"sub": user.email, "jti": jti, "type": "refresh", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def issue_tokens(db: Session, user: User) -> dict:
    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(db, user),
        "token_type": "bearer",
    }


def rotate_refresh_token(db: Session, refresh_token: str) -> dict:
    """Проверяет refresh-токен, отзывает старый, выдаёт новую пару."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise _credentials_exc
        jti = payload.get("jti")
        email = payload.get("sub")
    except JWTError:
        raise _credentials_exc

    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if row is None or row.is_revoked or row.expires_at < datetime.utcnow():
        raise _credentials_exc

    row.is_revoked = True
    db.commit()

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise _credentials_exc
    return issue_tokens(db, user)


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
    except JWTError:
        return
    row = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if row:
        row.is_revoked = True
        db.commit()


# текущий пользователь

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise _credentials_exc
        email = payload.get("sub")
        if email is None:
            raise _credentials_exc
    except JWTError:
        raise _credentials_exc

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise _credentials_exc
    return user
