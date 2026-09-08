import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.db.models import User, UserRole
from backend.db.session import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    username: str
    role: str


@router.post("/register", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()

    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên đăng nhập không được để trống")
    if len(username) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên đăng nhập phải có ít nhất 3 ký tự")
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu phải có ít nhất 6 ký tự")

    existing = db.query(User).filter_by(username=username).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tên đăng nhập đã tồn tại")

    # Ignore any role provided by the client. Public registrations must always be low-privilege
    # nurse accounts. Higher-privilege accounts are created via backend scripts or admin-only flows.
    user = User(username=username, hashed_password=hash_password(payload.password), role=UserRole.NURSE)
    db.add(user)
    db.commit()
    db.refresh(user)

    return MeResponse(id=user.id, username=user.username, role=user.role.value)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=payload.username).one_or_none()
    # Cố tình dùng CHUNG 1 thông báo lỗi cho "sai username" và "sai password" (không tiết lộ
    # username có tồn tại hay không - tránh dò tài khoản qua thông báo lỗi khác nhau).
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai tài khoản hoặc mật khẩu")
    if user is None:
        raise unauthorized
    try:
        password_ok = verify_password(payload.password, user.hashed_password)
    except ValueError:
        # bcrypt ném ValueError cho mật khẩu > 72 byte - vẫn là "sai mật khẩu", không phải lỗi server.
        raise unauthorized
    if not password_ok:
        raise unauthorized

    return LoginResponse(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        role=user.role.value,
    )


@router.post("/refresh", response_model=RefreshResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token không hợp lệ hoặc hết hạn")
    try:
        claims = decode_token(payload.refresh_token)
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

    return RefreshResponse(access_token=create_access_token(user))


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return MeResponse(id=current_user.id, username=current_user.username, role=current_user.role.value)
