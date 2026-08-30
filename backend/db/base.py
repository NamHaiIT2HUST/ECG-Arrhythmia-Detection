from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class chung cho toàn bộ ORM model (SQLAlchemy 2.0 declarative style).
    Alembic (`backend/db/migrations/env.py`) dùng `Base.metadata` để autogenerate migration,
    nên MỌI model mới phải kế thừa từ class này để được theo dõi."""
    pass
