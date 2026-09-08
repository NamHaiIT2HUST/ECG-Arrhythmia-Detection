"""
Validate that POST /api/auth/register always creates a `nurse` account even if client
sends role=admin/doctor. Uses TestClient against the app (no uvicorn needed).
Run: python -m backend.scripts.validate_register
"""
from fastapi.testclient import TestClient
from backend.main import app
from backend.scripts.seed_users import run as seed_run


def check(label, condition):
    print(f"[{'✓' if condition else '✗ THẤT BẠI'}] {label}")
    assert condition, f"Kiểm tra thất bại: {label}"


def run():
    # Ensure seed users exist for login sanity checks
    try:
        seed_run()
    except Exception:
        pass

    with TestClient(app) as client:
        username = "evil_admin"
        password = "Password@123"

        # 1. Try to register while requesting admin role
        res = client.post("/api/auth/register", json={"username": username, "password": password, "role": "admin"})
        check("Register request returns 201", res.status_code == 201)

        # 2. Login with created account
        res_login = client.post("/api/auth/login", json={"username": username, "password": password})
        check("Login with new account succeeds", res_login.status_code == 200)
        role = res_login.json().get("role")
        check("Role returned is 'nurse' (server-enforced)", role == "nurse")

        # 3. Try to register same username again -> 409
        res_dup = client.post("/api/auth/register", json={"username": username, "password": password})
        check("Duplicate register returns 409", res_dup.status_code == 409)

    print("\n[✓] Register enforcement checks passed.")


if __name__ == "__main__":
    run()
