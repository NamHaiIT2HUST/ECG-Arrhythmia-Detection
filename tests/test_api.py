import io

import numpy as np

from backend.db.models import AnomalyEvent
from backend.service.anomaly_log_service import get_or_create_default_patient, start_ecg_record

# ---------------------------------------------------------------------------
# GET /api/records
# ---------------------------------------------------------------------------

def test_get_records_shape(client):
    res = client.get("/api/records")
    assert res.status_code == 200
    body = res.json()
    assert "default_record" in body
    assert "count" in body
    assert isinstance(body["records"], list)


# ---------------------------------------------------------------------------
# POST /api/diagnosis/upload-ecg
# ---------------------------------------------------------------------------

def test_upload_diagnosis_shape(client):
    # Tín hiệu sin tổng hợp (không cần dữ liệu MIT-BIH thật) — chỉ để kiểm tra ĐÚNG SHAPE
    # response, không kiểm tra ý nghĩa lâm sàng của kết quả.
    signal = np.sin(np.linspace(0, 80, 3600))
    csv_bytes = io.BytesIO(("\n".join(f"{v:.4f}" for v in signal)).encode("utf-8"))

    res = client.post(
        "/api/diagnosis/upload-ecg?fs=360",
        files={"file": ("sample.csv", csv_bytes, "text/csv")},
    )
    assert res.status_code == 200
    body = res.json()
    for key in ("total_beats", "duration_seconds", "class_counts", "class_percentages",
                "bpm", "hrv", "anomalies", "anomalies_total", "anomalies_truncated", "overall_assessment"):
        assert key in body


def test_upload_diagnosis_rejects_too_short_file(client):
    csv_bytes = io.BytesIO(b"0.1\n0.2\n0.3\n")  # chỉ 3 mẫu, quá ngắn
    res = client.post(
        "/api/diagnosis/upload-ecg?fs=360",
        files={"file": ("tiny.csv", csv_bytes, "text/csv")},
    )
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Auth: POST /api/auth/login, POST /api/auth/refresh, GET /api/auth/me
# ---------------------------------------------------------------------------

def test_login_wrong_password_rejected(client, seeded_users):
    username = seeded_users["doctor"][0]
    res = client.post("/api/auth/login", json={"username": username, "password": "sai-mat-khau"})
    assert res.status_code == 401


def test_me_requires_valid_token(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer token-gia-mao"}).status_code == 401


def test_me_returns_correct_user(client, auth_headers, seeded_users):
    res = client.get("/api/auth/me", headers=auth_headers["doctor"])
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == seeded_users["doctor"][0]
    assert body["role"] == "doctor"


def test_refresh_rejects_access_token_used_as_refresh_token(client, auth_headers):
    login = client.post("/api/auth/login", json={"username": "doctor_test", "password": "Doctor@123"})
    access_token = login.json()["access_token"]
    res = client.post("/api/auth/refresh", json={"refresh_token": access_token})
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/anomalies, POST /api/anomalies/{id}/verify
# ---------------------------------------------------------------------------

def _seed_anomaly(test_session_factory, prediction_label="CẢNH BÁO: NHỊP THẤT (V)"):
    db = test_session_factory()
    try:
        patient = get_or_create_default_patient(db)
        record = start_ecg_record(db, patient.id, "208")
        event = AnomalyEvent(
            patient_id=patient.id, record_id=record.id, prediction_label=prediction_label,
            confidence=0.9, heatmap=None, r_peak_sample=100, timestamp_ms=1_700_000_000_000,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event.id
    finally:
        db.close()


def test_list_anomalies_requires_login(client):
    assert client.get("/api/anomalies").status_code == 401


def test_list_anomalies_filters_by_id(client, auth_headers, test_session_factory):
    anomaly_id = _seed_anomaly(test_session_factory)
    res = client.get(f"/api/anomalies?patient_id=999999999", headers=auth_headers["nurse"])
    assert res.status_code == 200
    assert res.json()["total"] == 0  # patient_id không tồn tại

    res = client.get("/api/anomalies", headers=auth_headers["nurse"])
    assert any(item["id"] == anomaly_id for item in res.json()["items"])


def test_verify_requires_doctor_or_admin_role(client, auth_headers, test_session_factory):
    anomaly_id = _seed_anomaly(test_session_factory)

    res = client.post(f"/api/anomalies/{anomaly_id}/verify", json={"status": "approved"},
                       headers=auth_headers["nurse"])
    assert res.status_code == 403

    res = client.post(f"/api/anomalies/{anomaly_id}/verify", json={"status": "approved"},
                       headers=auth_headers["doctor"])
    assert res.status_code == 200
    assert res.json()["review_status"] == "approved"


def test_verify_corrected_requires_valid_label(client, auth_headers, test_session_factory):
    anomaly_id = _seed_anomaly(test_session_factory)

    res = client.post(f"/api/anomalies/{anomaly_id}/verify", json={"status": "corrected"},
                       headers=auth_headers["doctor"])
    assert res.status_code == 422  # thiếu corrected_label

    res = client.post(f"/api/anomalies/{anomaly_id}/verify",
                       json={"status": "corrected", "corrected_label": "NHÃN BA LÁP"},
                       headers=auth_headers["doctor"])
    assert res.status_code == 422  # không thuộc 5 nhãn AAMI hợp lệ

    res = client.post(f"/api/anomalies/{anomaly_id}/verify",
                       json={"status": "corrected", "corrected_label": "BÌNH THƯỜNG"},
                       headers=auth_headers["doctor"])
    assert res.status_code == 200
    assert res.json()["corrected_label"] == "BÌNH THƯỜNG"


def test_verify_unknown_anomaly_returns_404(client, auth_headers):
    res = client.post("/api/anomalies/999999999/verify", json={"status": "approved"},
                       headers=auth_headers["admin"])
    assert res.status_code == 404
