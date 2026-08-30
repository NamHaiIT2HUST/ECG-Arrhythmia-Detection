from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.core.config import settings

# SQLite mặc định chỉ cho 1 thread dùng chung 1 connection; FastAPI chạy code đồng bộ
# (như route dùng Depends(get_db)) trên threadpool nên cần tắt check_same_thread.
# Không ảnh hưởng khi sau này đổi DATABASE_URL sang PostgreSQL (tham số bị bỏ qua).
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency cấp 1 Session dùng cho đúng 1 request rồi tự đóng lại.
    Dùng: `def route(db: Session = Depends(get_db)): ...`"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
