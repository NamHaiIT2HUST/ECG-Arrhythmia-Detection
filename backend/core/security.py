from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.models import User
from backend.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=True)


def hash_password(plain_password: str) -> str:
    """Băm mật khẩu bằng bcrypt trực tiếp (không qua passlib — passlib có xung đột phiên bản
    đã biết với bcrypt>=4.1, dùng thẳng thư viện `bcrypt` cho chắc chắn)."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def _create_token(claims: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = claims.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + expires_delta,
        "type": token_type,  # phân biệt access/refresh - bắt buộc kiểm tra lại khi decode
    })
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user: User) -> str:
    return _create_token(
        {"sub": str(user.id), "username": user.username, "role": user.role.value},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(user: User) -> str:
    # Refresh token chỉ mang "sub" (id) — role/username luôn được đọc LẠI từ DB lúc refresh,
    # tránh cấp access token mới mang role cũ nếu tài khoản bị đổi quyền sau khi đăng nhập.
    return _create_token(
        {"sub": str(user.id)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str) -> dict:
    """Giải mã + xác thực chữ ký/hạn JWT. Ném `jwt.InvalidTokenError` (bao gồm cả
    `ExpiredSignatureError`) nếu token sai chữ ký/hết hạn/sai định dạng — nơi gọi tự bắt."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: `current_user: User = Depends(get_current_user)`.
    401 nếu thiếu header, sai chữ ký, hết hạn, sai loại token (vd đưa refresh token vào đây),
    hoặc user đã bị xoá khỏi DB sau khi token được cấp."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise unauthorized

    if payload.get("type") != "access":
        raise unauthorized

    user_id = payload.get("sub")
    user = db.get(User, int(user_id)) if user_id is not None else None
    if user is None:
        raise unauthorized

    return user


def require_role(*roles: str):
    """Dependency factory phân quyền theo vai trò, dùng: `Depends(require_role("admin", "doctor"))`.
    So sánh theo string (vd "admin") để nơi gọi không cần import `UserRole`. 403 nếu vai trò
    không khớp (401 đã được `get_current_user` xử lý riêng cho trường hợp chưa đăng nhập)."""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu vai trò: {', '.join(roles)}",
            )
        return current_user
    return checker
