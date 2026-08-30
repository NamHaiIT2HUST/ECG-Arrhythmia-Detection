"""
Kiem chung end-to-end CP5.2 (login/refresh/me + phan quyen require_role) theo dung contract
da co dinh trong plan.md muc 5.3, dung FastAPI TestClient (khong can chay uvicorn that).

Yeu cau: da chay `python -m backend.scripts.seed_users` truoc do de co san 3 tai khoan test.
Chay: python -m backend.scripts.validate_auth
"""
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.core.security import require_role
from backend.main import app as real_app


def check(label, condition):
    print(f"[{'✓' if condition else '✗ THẤT BẠI'}] {label}")
    assert condition, f"Kiểm tra thất bại: {label}"


def run():
    # Dùng context manager để đảm bảo `lifespan` (nạp model ResNet1D) chạy đúng 1 lần
    # trước request đầu tiên, giống hệt khi chạy `uvicorn backend.main:app` thật.
    with TestClient(real_app) as client:
        _run_checks(client)


def _run_checks(client):
    # 1. Login đúng -> 200 + đủ field theo đúng contract
    res = client.post("/api/auth/login", json={"username": "bs_hai", "password": "Doctor@123"})
    check("POST /api/auth/login (đúng mật khẩu) trả 200", res.status_code == 200)
    body = res.json()
    for field in ("access_token", "refresh_token", "token_type", "role"):
        check(f"  response có field '{field}'", field in body)
    check("  role đúng = doctor", body.get("role") == "doctor")
    access_token = body["access_token"]
    refresh_token = body["refresh_token"]

    # 2. Sai mật khẩu -> 401
    res = client.post("/api/auth/login", json={"username": "bs_hai", "password": "sai-mat-khau"})
    check("POST /api/auth/login (sai mật khẩu) trả 401", res.status_code == 401)

    # 3. Sai username -> vẫn 401 (không tiết lộ username có tồn tại hay không)
    res = client.post("/api/auth/login", json={"username": "khong_ton_tai", "password": "abc"})
    check("POST /api/auth/login (sai username) trả 401", res.status_code == 401)

    # 4. GET /api/auth/me với access token đúng -> trả đúng user
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    check("GET /api/auth/me (token hợp lệ) trả 200", res.status_code == 200)
    me = res.json()
    check("  username đúng = bs_hai", me.get("username") == "bs_hai")
    check("  role đúng = doctor", me.get("role") == "doctor")

    # 5. GET /api/auth/me không có token -> 401
    res = client.get("/api/auth/me")
    check("GET /api/auth/me (không có token) trả 401", res.status_code == 401)

    # 6. GET /api/auth/me với token rác -> 401
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer token-gia-mao"})
    check("GET /api/auth/me (token giả) trả 401", res.status_code == 401)

    # 7. POST /api/auth/refresh với refresh token đúng -> access token mới dùng được
    res = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    check("POST /api/auth/refresh (refresh token hợp lệ) trả 200", res.status_code == 200)
    new_access_token = res.json().get("access_token")
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access_token}"})
    check("  access token mới dùng được cho /api/auth/me", res.status_code == 200)

    # 8. Dùng NHẦM access token làm refresh token -> phải bị từ chối (kiểm tra claim "type")
    res = client.post("/api/auth/refresh", json={"refresh_token": access_token})
    check("POST /api/auth/refresh (đưa nhầm access token) trả 401", res.status_code == 401)

    # 9. require_role: dùng 1 route test riêng (không đụng vào app thật - main.py chỉ có
    # đúng 3 endpoint auth theo contract, không thêm route thử nghiệm vào đó)
    test_app = FastAPI()

    @test_app.get("/test/admin-only")
    def admin_only(user=Depends(require_role("admin"))):
        return {"ok": True}

    test_client = TestClient(test_app)

    res = test_client.get("/test/admin-only", headers={"Authorization": f"Bearer {access_token}"})
    check("require_role('admin') từ chối token role=doctor (403)", res.status_code == 403)

    admin_login = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
    admin_token = admin_login.json()["access_token"]
    res = test_client.get("/test/admin-only", headers={"Authorization": f"Bearer {admin_token}"})
    check("require_role('admin') chấp nhận token role=admin (200)", res.status_code == 200)

    print("\n[✓] CP 5.2 — toàn bộ kiểm tra end-to-end đều đạt.")


if __name__ == "__main__":
    run()
