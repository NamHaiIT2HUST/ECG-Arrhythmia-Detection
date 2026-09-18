from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.security import hash_password, require_role
from backend.db.models import AnomalyEvent, User, UserRole
from backend.db.session import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])

VALID_ROLES = {r.value for r in UserRole}


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str


class StatsResponse(BaseModel):
    users_by_role: dict[str, int]
    total_anomalies: int


@router.get("/users", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """CP mới: chỉ admin xem được danh sách toàn bộ tài khoản trong hệ thống."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserOut(id=u.id, username=u.username, role=u.role.value, created_at=u.created_at) for u in users]


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """CP mới: thay thế hoàn toàn `/api/auth/register` (đã xoá) — trong triển khai thật, chỉ
    admin được tạo tài khoản mới, và admin tự chọn đúng vai trò (không bị ép cứng về nurse
    như luồng tự đăng ký công khai cũ)."""
    username = payload.username.strip()

    if not username or len(username) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên đăng nhập phải có ít nhất 3 ký tự")
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mật khẩu phải có ít nhất 6 ký tự")
    if payload.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vai trò không hợp lệ, phải là 1 trong: {sorted(VALID_ROLES)}",
        )

    existing = db.query(User).filter_by(username=username).one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tên đăng nhập đã tồn tại")

    user = User(username=username, hashed_password=hash_password(payload.password), role=UserRole(payload.role))
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(id=user.id, username=user.username, role=user.role.value, created_at=user.created_at)


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Thống kê tổng quan cho màn Admin: số tài khoản theo từng vai trò + tổng số sự kiện bất
    thường AI đã ghi nhận (dữ liệu thật từ DB — không tính số bệnh nhân ở đây vì Patient hiện
    vẫn quản lý ở localStorage phía frontend, chưa có API thật — xem `usePatient()`)."""
    counts = dict(db.query(User.role, func.count(User.id)).group_by(User.role).all())
    users_by_role = {role.value: 0 for role in UserRole}
    for role, count in counts.items():
        users_by_role[role.value] = count

    total_anomalies = db.query(AnomalyEvent).count()

    return StatsResponse(users_by_role=users_by_role, total_anomalies=total_anomalies)
