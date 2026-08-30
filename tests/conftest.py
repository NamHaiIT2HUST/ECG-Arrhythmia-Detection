"""
Fixture dung chung cho toan bo pytest suite (CP6.2).

Quan trong: KHONG dung DB dev that (backend/db/ecg_system.db) cho test - moi test session
dung 1 file SQLite TAM RIENG (tu xoa sau khi chay xong), dam bao pytest khong lam ban/phu
thuoc du lieu dev that va nguoc lai. Ghi de dependency `get_db` cua FastAPI bang
`app.dependency_overrides` (co che chuan cua FastAPI cho testing, khong sua code production).

`client` va cac fixture phu thuoc no la SESSION-SCOPED (dung chung 1 lan cho ca session pytest)
vi lifespan cua app nap model ResNet1D ~1-2s - lam lai cho tung test se rat cham.
"""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.security import hash_password
from backend.db.base import Base
from backend.db.models import User, UserRole
from backend.db.session import get_db
from backend.main import app

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cac test can du lieu MIT-BIH that (data/raw/, gitignored) se tu skip neu thieu - dung
# tren CI (GitHub Actions) khong co san 2 thu muc nay, xem plan.md muc 6.4.
HAS_PHYSIONET_DATA = os.path.isdir(os.path.join(ROOT_DIR, "data", "raw", "physionet_mitdb"))
HAS_SAVED_MODEL = os.path.isfile(os.path.join(ROOT_DIR, "saved_models", "resnet1d.pth"))
HAS_ONNX_MODEL = os.path.isfile(os.path.join(ROOT_DIR, "saved_models", "resnet1d.onnx"))

requires_physionet_data = pytest.mark.skipif(
    not HAS_PHYSIONET_DATA, reason="Thiếu data/raw/physionet_mitdb/ (gitignored, tự tải về nếu cần)"
)
requires_saved_model = pytest.mark.skipif(
    not HAS_SAVED_MODEL, reason="Thiếu saved_models/resnet1d.pth (gitignored, chạy `python src/benchmark.py` để tạo)"
)
requires_onnx_model = pytest.mark.skipif(
    not HAS_ONNX_MODEL, reason="Chưa export ONNX (chạy `python -m src.models.export_onnx` trước)"
)

TEST_USERS = {
    "admin": ("admin_test", "Admin@123", UserRole.ADMIN),
    "doctor": ("doctor_test", "Doctor@123", UserRole.DOCTOR),
    "nurse": ("nurse_test", "Nurse@123", UserRole.NURSE),
}


@pytest.fixture(scope="session")
def test_session_factory():
    # SQLite ":memory:" bình thường tạo 1 DB rỗng MỚI cho mỗi connection - phải ép dùng
    # chung đúng 1 connection (StaticPool) để mọi session trong suốt phiên test đọc/ghi
    # cùng 1 dữ liệu. Dùng in-memory (không phải file tmp) để tránh lỗi quyền thư mục temp
    # từng gặp trên Windows (tmp_path_factory) và không cần dọn file sau khi chạy xong.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def client(test_session_factory):
    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def seeded_users(test_session_factory):
    db = test_session_factory()
    try:
        for username, password, role in TEST_USERS.values():
            if db.query(User).filter_by(username=username).one_or_none() is None:
                db.add(User(username=username, hashed_password=hash_password(password), role=role))
        db.commit()
    finally:
        db.close()
    return TEST_USERS


@pytest.fixture(scope="session")
def auth_headers(client, seeded_users):
    """Tra ve {"admin": {...}, "doctor": {...}, "nurse": {...}} - moi gia tri la header
    Authorization Bearer dung de goi thang vao request cua test khac."""
    headers = {}
    for role_name, (username, password, _role) in seeded_users.items():
        res = client.post("/api/auth/login", json={"username": username, "password": password})
        assert res.status_code == 200, f"Seed login thất bại cho {username}: {res.text}"
        headers[role_name] = {"Authorization": f"Bearer {res.json()['access_token']}"}
    return headers
