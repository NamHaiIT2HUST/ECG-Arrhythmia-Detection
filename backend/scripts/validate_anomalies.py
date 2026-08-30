"""
Kiem chung end-to-end CP5.3: mo 1 phien WebSocket THAT (record 208, nhieu PVC) de
ws_routes.py tu ghi cac su kien bat thuong that vao Database, roi goi GET /api/anomalies
kiem tra xac thuc + loc theo patient_id/nhan/thoi gian + phan trang co dung khong.

Yeu cau: da chay `python -m backend.scripts.seed_users` truoc do.
Chay: python -m backend.scripts.validate_anomalies
Luu y: mo WS that nen mat khoang 8-10 giay (300 goi tin x ~28ms) de co du lieu that, khong
the rut ngan hon ma van dam bao co it nhat 1 nhip bat thuong that duoc ghi vao DB.
"""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.main import app


def check(label, condition):
    print(f"[{'✓' if condition else '✗ THẤT BẠI'}] {label}")
    assert condition, f"Kiểm tra thất bại: {label}"


def run():
    with TestClient(app) as client:
        login = client.post("/api/auth/login", json={"username": "bs_hai", "password": "Doctor@123"})
        check("Login lấy token thành công", login.status_code == 200)
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # 1. Chưa có token -> 401
        res = client.get("/api/anomalies")
        check("GET /api/anomalies không có token trả 401", res.status_code == 401)

        # 2. Mở 1 phiên WS thật để tạo dữ liệu anomaly_events thật trong DB
        print("[i] Đang mở WebSocket thật (record 208) để sinh dữ liệu, mất khoảng 8-10 giây...")
        beats_seen = 0
        with client.websocket_connect("/ws/ecg?record=208") as ws:
            for _ in range(300):
                if ws.receive_json().get("is_new_beat"):
                    beats_seen += 1
        check(f"Stream WS phát hiện được nhịp tim mới ({beats_seen} nhịp / 300 gói tin)", beats_seen > 0)

        # 3. Query không lọc -> phải có ít nhất 1 kết quả (record 208 chắc chắn có PVC)
        res = client.get("/api/anomalies", headers=headers)
        check("GET /api/anomalies (không lọc) trả 200", res.status_code == 200)
        body = res.json()
        check("  có ít nhất 1 sự kiện đã ghi vào DB", body["total"] > 0)
        check("  page/page_size mặc định đúng (1/20)", body["page"] == 1 and body["page_size"] == 20)
        check("  số item trả về <= page_size", len(body["items"]) <= body["page_size"])

        first_item = body["items"][0]
        for field in ("id", "patient_id", "record_id", "prediction_label", "confidence",
                      "r_peak_sample", "timestamp_ms", "review_status"):
            check(f"  item có field '{field}'", field in first_item)
        check("  review_status mặc định = pending", first_item["review_status"] == "pending")
        if len(body["items"]) > 1:
            check("  sắp xếp mới nhất trước (timestamp_ms giảm dần)",
                  body["items"][0]["timestamp_ms"] >= body["items"][-1]["timestamp_ms"])

        # 4. Lọc theo đúng patient_id của sự kiện vừa tạo
        patient_id = first_item["patient_id"]
        res = client.get("/api/anomalies", params={"patient_id": patient_id}, headers=headers)
        check("GET /api/anomalies?patient_id=<đúng> trả 200", res.status_code == 200)
        items = res.json()["items"]
        check("  mọi item đều đúng patient_id đã lọc", all(it["patient_id"] == patient_id for it in items))

        # 5. Lọc theo patient_id không tồn tại -> 0 kết quả
        res = client.get("/api/anomalies", params={"patient_id": 999999}, headers=headers)
        check("  patient_id không tồn tại trả total=0", res.json()["total"] == 0)

        # 6. Lọc đúng theo nhãn của sự kiện đầu tiên
        label = first_item["prediction_label"]
        res = client.get("/api/anomalies", params={"label": label}, headers=headers)
        items = res.json()["items"]
        check(f"GET /api/anomalies?label={label!r} trả toàn item đúng nhãn",
              len(items) > 0 and all(it["prediction_label"] == label for it in items))

        # 7. Lọc theo nhãn không tồn tại -> 0 kết quả
        res = client.get("/api/anomalies", params={"label": "NHÃN KHÔNG TỒN TẠI"}, headers=headers)
        check("  nhãn không tồn tại trả total=0", res.json()["total"] == 0)

        # 8. Lọc theo khoảng thời gian TƯƠNG LAI (chưa xảy ra) -> 0 kết quả
        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        res = client.get("/api/anomalies", params={"from": future}, headers=headers)
        check("  lọc from=tương lai trả total=0", res.json()["total"] == 0)

        # 9. Lọc theo khoảng thời gian quá khứ xa -> vẫn thấy dữ liệu vừa tạo
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        res = client.get("/api/anomalies", params={"from": past}, headers=headers)
        check("  lọc from=quá khứ xa vẫn thấy dữ liệu vừa tạo", res.json()["total"] > 0)

        # 10. Phân trang: page_size=1 phải chỉ trả đúng 1 item, total không đổi
        res_all = client.get("/api/anomalies", headers=headers).json()
        res_p1 = client.get("/api/anomalies", params={"page_size": 1, "page": 1}, headers=headers).json()
        check("Phân trang page_size=1 trả đúng 1 item", len(res_p1["items"]) == 1)
        check("  total không đổi khi phân trang", res_p1["total"] == res_all["total"])
        if res_all["total"] > 1:
            res_p2 = client.get("/api/anomalies", params={"page_size": 1, "page": 2}, headers=headers).json()
            check("  page 2 khác page 1 (không lặp lại cùng 1 item)",
                  res_p2["items"][0]["id"] != res_p1["items"][0]["id"])

    print("\n[✓] CP 5.3 — toàn bộ kiểm tra end-to-end đều đạt.")


if __name__ == "__main__":
    run()
