"""
Tao san 3 tai khoan test (1 cho moi role: admin/doctor/nurse) de Track Frontend (CP5.5) test
du 3 role ngay khong can tu tao qua API - he thong nay khong co endpoint tu dang ky cong khai
(dung noi bo cho benh vien, tai khoan do Admin/script tao san), dung backend/scripts/seed_users.py
la cach duy nhat de co user dau tien.

Chay: python -m backend.scripts.seed_users
Idempotent: chay lai nhieu lan khong tao trung username (bo qua neu da ton tai).
"""
from backend.core.security import hash_password
from backend.db.models import User, UserRole
from backend.db.session import SessionLocal

# username, password, role - password de doc (khong dung cho production that)
SEED_USERS = [
    ("admin", "Admin@123", UserRole.ADMIN),
    ("bs_hai", "Doctor@123", UserRole.DOCTOR),
    ("dd_lan", "Nurse@123", UserRole.NURSE),
]


def run():
    db = SessionLocal()
    try:
        for username, password, role in SEED_USERS:
            if db.query(User).filter_by(username=username).one_or_none() is not None:
                print(f"[i] Bỏ qua, đã tồn tại: {username}")
                continue
            db.add(User(username=username, hashed_password=hash_password(password), role=role))
            print(f"[✓] Đã tạo: {username} / {password}  (role={role.value})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
