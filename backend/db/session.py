from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.core.config import settings

from sqlalchemy import event

# SQLite mặc định chỉ cho 1 thread dùng chung 1 connection; FastAPI chạy code đồng bộ
# (như route dùng Depends(get_db)) trên threadpool nên cần tắt check_same_thread.
# Bổ sung timeout=30.0 để tránh OperationalError: database is locked khi stream dài hoặc đa luồng.
connect_args = {"check_same_thread": False, "timeout": 30.0} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency cấp 1 Session dùng cho đúng 1 request rồi tự đóng lại.
    Dùng: `def route(db: Session = Depends(get_db)): ...`"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
