from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.models import User
from backend.db.session import get_db


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _create_token(claims: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = claims.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": token_type,
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "username": user.username, "role": user.role.value},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def create_ws_ticket(user: User) -> str:
    return _create_token(
        {"sub": str(user.id)},
        timedelta(seconds=10),
        token_type="ws_ticket",
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc hết hạn",
    )
    if not token:
        raise unauthorized

    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError:
        raise unauthorized

    if payload.get("type") != "access":
        raise unauthorized

    user_id = payload.get("sub")
    try:
        user = db.get(User, int(user_id)) if user_id is not None else None
    except (ValueError, TypeError):
        raise unauthorized
    if user is None:
        raise unauthorized

    return user


def get_user_from_ws_ticket(ticket: str | None, db: Session) -> User | None:
    if not ticket:
        return None
    try:
        payload = decode_token(ticket)
    except jwt.InvalidTokenError:
        return None
    if payload.get("type") != "ws_ticket":
        return None
    user_id = payload.get("sub")
    try:
        user = db.get(User, int(user_id)) if user_id is not None else None
    except (ValueError, TypeError):
        return None
    return user


def require_role(*roles: str):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu vai trò: {
.join(roles)}",
            )
        return current_user
    return checker

