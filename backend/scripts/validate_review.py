"""
Kiem chung end-to-end CP5.4: bac si/admin xac nhan hoac sua nhan 1 su kien bat thuong
(Human-in-the-loop), kiem tra phan quyen (doctor/admin duoc phep, nurse bi tu choi),
validate corrected_label, va audit trail duoc ghi dung.

Yeu cau: da chay `python -m backend.scripts.seed_users` truoc do.
Chay: python -m backend.scripts.validate_review
"""
from fastapi.testclient import TestClient

from backend.db.models import AnomalyEvent, AuditTrail
from backend.db.session import SessionLocal
from backend.main import app
from backend.service.anomaly_log_service import get_or_create_default_patient, start_ecg_record


def check(label, condition):
    print(f"[{'✓' if condition else '✗ THẤT BẠI'}] {label}")
    assert condition, f"Kiểm tra thất bại: {label}"


def _seed_test_anomaly() -> int:
    """Tạo trực tiếp 1 dòng anomaly_events qua ORM (không cần mở WebSocket thật —
    đường dây đó đã được validate_anomalies.py kiểm chứng riêng) để test /verify nhanh + xác định."""
    db = SessionLocal()
    try:
        patient = get_or_create_default_patient(db)
        record = start_ecg_record(db, patient.id, "208")
        event = AnomalyEvent(
            patient_id=patient.id, record_id=record.id,
            prediction_label="CẢNH BÁO: NHỊP THẤT (V)", confidence=0.95,
            heatmap=None, r_peak_sample=209, timestamp_ms=1_700_000_000_000,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event.id
    finally:
        db.close()


def run():
    anomaly_id = _seed_test_anomaly()

    with TestClient(app) as client:
        def login(username, password):
            res = client.post("/api/auth/login", json={"username": username, "password": password})
            return res.json()["access_token"]

        doctor_token = login("bs_hai", "Doctor@123")
        nurse_token = login("dd_lan", "Nurse@123")
        admin_token = login("admin", "Admin@123")

        def verify(token, body):
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            return client.post(f"/api/anomalies/{anomaly_id}/verify", json=body, headers=headers)

        # 1. Nurse KHÔNG được verify -> 403
        check("Nurse verify bị từ chối (403)", verify(nurse_token, {"status": "approved"}).status_code == 403)

        # 2. Không có token -> 401
        check("Không có token trả 401", verify(None, {"status": "approved"}).status_code == 401)

        # 3. Doctor duyệt (approved) -> 200, review_status đổi đúng
        res = verify(doctor_token, {"status": "approved"})
        check("Doctor verify (approved) trả 200", res.status_code == 200)
        body = res.json()
        check("  review_status = approved", body["review_status"] == "approved")
        check("  corrected_label = None khi approved", body["corrected_label"] is None)
        check("  reviewed_by đã được gán", body["reviewed_by"] is not None)

        # 4. Sửa nhãn (corrected) thiếu corrected_label -> 422
        check("corrected thiếu corrected_label trả 422",
              verify(doctor_token, {"status": "corrected"}).status_code == 422)

        # 5. Sửa nhãn với label không hợp lệ -> 422
        check("corrected_label không hợp lệ (không thuộc 5 lớp AAMI) trả 422",
              verify(doctor_token, {"status": "corrected", "corrected_label": "NHÃN BA LÁP"}).status_code == 422)

        # 6. Sửa nhãn đúng -> 200
        res = verify(doctor_token, {"status": "corrected", "corrected_label": "BÌNH THƯỜNG"})
        check("Doctor verify (corrected hợp lệ) trả 200", res.status_code == 200)
        body = res.json()
        check("  review_status = corrected", body["review_status"] == "corrected")
        check("  corrected_label = BÌNH THƯỜNG", body["corrected_label"] == "BÌNH THƯỜNG")

        # 7. Admin cũng được verify
        check("Admin verify được (200)", verify(admin_token, {"status": "approved"}).status_code == 200)

        # 8. id không tồn tại -> 404
        res = client.post("/api/anomalies/999999999/verify", json={"status": "approved"},
                           headers={"Authorization": f"Bearer {doctor_token}"})
        check("Verify id không tồn tại trả 404", res.status_code == 404)

    # 9. Kiểm tra audit_trails đã ghi đủ (3 lần verify THÀNH CÔNG: approved, corrected, approved)
    db = SessionLocal()
    try:
        logs = db.query(AuditTrail).filter_by(target_type="anomaly_event", target_id=anomaly_id).all()
        check(f"audit_trails ghi đủ 3 lần verify thành công (thấy {len(logs)})", len(logs) == 3)
        check("  action đúng = anomaly.verify", all(log.action == "anomaly.verify" for log in logs))
        check("  user_id được ghi cho mọi audit log", all(log.user_id is not None for log in logs))
    finally:
        db.close()

    print("\n[✓] CP 5.4 — toàn bộ kiểm tra end-to-end đều đạt.")


if __name__ == "__main__":
    run()
