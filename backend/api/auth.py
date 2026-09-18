import time
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.security import (
    create_access_token,
    create_refresh_token,
    create_ws_ticket,
    decode_token,
    get_current_user,
    verify_password,
)
from backend.core.config import settings
from backend.db.models import User
from backend.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory rate limiter for login
# Key: IP address, Value: list of timestamps
login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPTS_WINDOW_SECONDS = 60

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    if client_ip not in login_attempts:
        login_attempts[client_ip] = []
        
    # Remove old attempts
    login_attempts[client_ip] = [t for t in login_attempts[client_ip] if now - t < LOGIN_ATTEMPTS_WINDOW_SECONDS]
    
    if len(login_attempts[client_ip]) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Quá nhiều lần đăng nhập sai. Vui lòng thử lại sau.")
        
    login_attempts[client_ip].append(now)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    role: str


class MeResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str


class WsTicketResponse(BaseModel):
    ticket: str


def set_auth_cookies(response: Response, access_token: str, refresh_token: str | None = None):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True, # Require HTTPS in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )


@router.post("/login", response_model=LoginResponse)
def login(request: Request, response: Response, payload: LoginRequest, db: Session = Depends(get_db)):
    check_rate_limit(request)

    user = db.query(User).filter_by(username=payload.username).one_or_none()
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai tài khoản hoặc mật khẩu")
    if user is None:
        raise unauthorized
    try:
        password_ok = verify_password(payload.password, user.hashed_password)
    except ValueError:
        raise unauthorized
    if not password_ok:
        raise unauthorized

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(role=user.role.value)


@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ hoặc hết hạn")
    
    if not refresh_token:
        raise unauthorized

    try:
        claims = decode_token(refresh_token)
    except jwt.InvalidTokenError:
        raise unauthorized

    if claims.get("type") != "refresh":
        raise unauthorized

    user_id = claims.get("sub")
    try:
        user = db.get(User, int(user_id)) if user_id is not None else None
    except (ValueError, TypeError):
        raise unauthorized
    if user is None:
        raise unauthorized

    new_access_token = create_access_token(user)
    set_auth_cookies(response, new_access_token)

    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")
    return {"ok": True}


@router.post("/ws-ticket", response_model=WsTicketResponse)
def get_ws_ticket(current_user: User = Depends(get_current_user)):
    ticket = create_ws_ticket(current_user)
    return WsTicketResponse(ticket=ticket)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return MeResponse(id=current_user.id, username=current_user.username, full_name=current_user.full_name, role=current_user.role.value)

