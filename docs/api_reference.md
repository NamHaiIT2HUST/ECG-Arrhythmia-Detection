# API Reference

Tài liệu tham chiếu toàn bộ endpoint (WebSocket + REST) của backend FastAPI. Xem kiến trúc
tổng quan tại [architecture.md](architecture.md), lộ trình phát triển tại [plan.md](../plan.md).

> Khi backend đang chạy, FastAPI tự sinh tài liệu tương tác đầy đủ (thử request trực tiếp từ
> trình duyệt) tại `http://localhost:8000/docs` (Swagger UI) hoặc `/redoc`. Tài liệu dưới đây
> là bản tóm tắt tĩnh, dễ đọc/tìm kiếm hơn khi không có server chạy sẵn.

**Base URL (dev)**: `http://localhost:8000` (đổi CORS/host qua `backend/core/config.py` hoặc biến môi trường — xem [deployment_guide.md](deployment_guide.md)).

## Xác thực (Authentication)

Toàn bộ endpoint REST dưới `/api/anomalies` yêu cầu header:
```
Authorization: Bearer <access_token>
```
Lấy `access_token` từ `POST /api/auth/login`. `GET /api/records`, `POST /api/diagnosis/upload-ecg`, và `WS /ws/ecg` **không yêu cầu đăng nhập** (chưa làm phân quyền cho các endpoint này — có thể là việc mở rộng CP5 sau này nếu cần).

3 tài khoản test có sẵn (tạo bằng `python -m backend.scripts.seed_users`):

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@123` | admin |
| `bs_hai` | `Doctor@123` | doctor |
| `dd_lan` | `Nurse@123` | nurse |

---

## `GET /`

Health check đơn giản, không cần auth.

**200**:
```json
{ "message": "Trái tim hệ thống ECG đang đập bình thường! 💓", "websocket_endpoint": "ws://localhost:8000/ws/ecg", "status": "online" }
```

---

## Auth — `backend/api/auth.py`

### `POST /api/auth/login`
**Body**: `{ "username": string, "password": string }`

**200**:
```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "role": "admin" }
```
**401**: `{ "detail": "Sai tài khoản hoặc mật khẩu" }` (dùng chung 1 thông báo cho cả sai username lẫn sai password, tránh lộ username nào tồn tại).

Access token hết hạn sau 30 phút (`ACCESS_TOKEN_EXPIRE_MINUTES`), refresh token sau 7 ngày (`REFRESH_TOKEN_EXPIRE_DAYS`) — cấu hình trong `backend/core/config.py`.

### `POST /api/auth/refresh`
**Body**: `{ "refresh_token": string }`

**200**: `{ "access_token": "...", "token_type": "bearer" }`
**401**: token không hợp lệ/hết hạn, hoặc lỡ đưa access token vào chỗ refresh token (server kiểm tra claim `type` bên trong JWT).

Role trong access token mới luôn được đọc lại từ DB tại thời điểm refresh (không dùng role cũ lúc đăng nhập), để phản ánh đúng nếu tài khoản vừa bị đổi quyền.

### `GET /api/auth/me`
**Header**: `Authorization: Bearer <access_token>`

**200**: `{ "id": int, "username": string, "role": string }`
**401**: thiếu token / token không hợp lệ / hết hạn.

---

## Records — `backend/api/records_routes.py`

### `GET /api/records`
Không cần auth. Quét `data/raw/physionet_mitdb/` (mọi cặp file `.hea`+`.dat`), trả danh sách bản ghi PhysioNet khả dụng kèm mô tả lâm sàng cho các bản ghi tiêu biểu.

**200**:
```json
{
  "default_record": "208",
  "count": 48,
  "records": [
    { "id": "100", "description": "Nhịp xoang bình thường - phù hợp demo baseline", "is_default": false },
    { "id": "208", "description": "Ngoại tâm thu thất (PVC) tần suất rất cao (mặc định khi stream)", "is_default": true }
  ]
}
```
Dùng `id` làm giá trị query param `record` khi mở WebSocket bên dưới.

---

## WebSocket Streaming — `backend/api/ws_routes.py`

### `WS /ws/ecg?record=<id>&patient_id=<id>`
Không cần auth. Stream real-time tín hiệu ECG (đọc từ file PhysioNet mô phỏng máy đo), 10 điểm/gói tin, 36 gói/giây (≈ 360Hz).

**Query params** (đều tuỳ chọn):
- `record` (string, mặc định `"208"`): id bản ghi PhysioNet, lấy từ `GET /api/records`. Nếu không tồn tại, tự dùng bản ghi mặc định (không lỗi).
- `patient_id` (int, mặc định không có): gắn phiên stream với 1 bệnh nhân trong DB để log sự kiện bất thường đúng người. Không truyền hoặc truyền id không tồn tại → tự dùng "bệnh nhân mặc định" (không lỗi, không chặn — xem `plan.md` mục 5.4 để biết lý do thiết kế).

**Mỗi message JSON gửi về**:
```jsonc
{
  "chunk": [10 float],           // điểm tín hiệu mới (đã lọc nhiễu) để vẽ tiếp biểu đồ
  "prediction": "BÌNH THƯỜNG" | "CẢNH BÁO: TRÊN THẤT (S)" | "CẢNH BÁO: NHỊP THẤT (V)" | "CẢNH BÁO: HỢP NHẤT (F)" | "CẢNH BÁO: CHƯA RÕ (Q)" | "CHỜ DỮ LIỆU",
  "heatmap": [187 float] | null,  // CHỈ khác null đúng ở gói tin vừa phát hiện 1 nhịp bất thường mới
  "latency_ms": float,           // độ trễ suy luận AI của lần chẩn đoán gần nhất
  "confidence": float,           // xác suất softmax của nhãn dự đoán gần nhất (0-1)
  "bpm": float,                  // nhịp tim tức thời theo khoảng RR thực tế
  "hrv_sdnn": float,             // HRV - SDNN (ms), cửa sổ trượt tối đa 50 nhịp gần nhất
  "hrv_rmssd": float,            // HRV - RMSSD (ms)
  "is_new_beat": boolean         // true đúng lúc gói tin này vừa chẩn đoán 1 nhịp mới
}
```
`prediction`/`bpm`/`hrv_sdnn`/`hrv_rmssd`/`latency_ms`/`confidence` được **giữ nguyên giữa 2 nhịp** (sample-and-hold) — chỉ thực sự đổi giá trị khi `is_new_beat=true`. `heatmap` thì ngược lại: về `null` ngay ở gói tin kế tiếp.

Mỗi nhịp bất thường (`heatmap != null`) tự động được ghi vào bảng `anomaly_events` trong DB — xem lại qua `GET /api/anomalies` bên dưới.

---

## Diagnosis (Offline) — `backend/api/diagnosis_routes.py`

### `POST /api/diagnosis/upload-ecg?fs=360`
Không cần auth. Nhận file CSV (1 cột biên độ tín hiệu ECG, có/không header, lấy **cột cuối** nếu file nhiều cột), chạy toàn bộ pipeline (lọc nhiễu → phát hiện đỉnh R → cắt nhịp → AI) trên **TOÀN BỘ** nhịp phát hiện được, trả về báo cáo tổng hợp — không phải luồng real-time.

**Query param**: `fs` (int, mặc định 360, 50-2000) — tần số lấy mẫu của file.
**Body**: `multipart/form-data`, field `file`.

**200**:
```jsonc
{
  "total_beats": int,
  "duration_seconds": float,
  "class_counts": { "BÌNH THƯỜNG": int, "CẢNH BÁO: NHỊP THẤT (V)": int, ... },
  "class_percentages": { "BÌNH THƯỜNG": 62.5, ... },
  "bpm": { "avg": float, "min": float, "max": float },
  "hrv": { "sdnn_ms": float, "rmssd_ms": float },
  "anomalies": [ { "beat_index": int, "r_peak_sample": int, "time_seconds": float, "prediction": str, "confidence": float } ],  // tối đa 500 mục
  "anomalies_total": int,
  "anomalies_truncated": bool,   // true nếu số nhịp bất thường thật > 500 (danh sách bị cắt bớt)
  "overall_assessment": "Phát hiện X/Y nhịp bất thường (Z%), chủ yếu là '...' (N nhịp)."  // rule-based, KHÔNG phải LLM
}
```
**400**: file rỗng, không parse được giá trị hợp lệ nào, hoặc ngắn hơn 2 giây dữ liệu tại `fs` đã khai báo.
**503**: model AI chưa sẵn sàng (hiếm gặp, chỉ khi backend vừa khởi động xong nhưng chưa nạp xong model).

Không trả `heatmap` cho từng nhịp (tránh payload phình to với file dài) — muốn xem XAI chi tiết 1 nhịp thì dùng luồng real-time (`WS /ws/ecg`).

---

## Anomalies (Lịch sử & Human-in-the-loop) — `backend/api/anomalies.py`

### `GET /api/anomalies`
**Yêu cầu**: đăng nhập (mọi role).

**Query params** (đều tuỳ chọn):
- `patient_id` (int)
- `from`, `to` (ISO 8601, vd `2026-08-30T00:00:00Z`; không có timezone thì coi như UTC)
- `label` (string, khớp chính xác 1 trong 5 nhãn AAMI, vd `"CẢNH BÁO: NHỊP THẤT (V)"`)
- `page` (int, mặc định 1), `page_size` (int, mặc định 20, tối đa 200)

**200**:
```jsonc
{
  "total": int, "page": int, "page_size": int,
  "items": [
    {
      "id": int, "patient_id": int, "record_id": int,
      "prediction_label": str, "confidence": float | null,
      "r_peak_sample": int | null, "timestamp_ms": int,
      "review_status": "pending" | "approved" | "corrected",
      "reviewed_by": int | null, "corrected_label": str | null
    }
  ]
}
```
Sắp xếp `timestamp_ms` giảm dần (mới nhất trước). Không trả `heatmap`.

### `POST /api/anomalies/{id}/verify`
**Yêu cầu**: đăng nhập với role `doctor` hoặc `admin` (nurse bị từ chối).

**Body**: `{ "status": "approved" | "corrected", "corrected_label"?: string }`
- `corrected_label` **bắt buộc** khi `status="corrected"`, và phải là 1 trong 5 nhãn AAMI hợp lệ.

**200**: trả về `AnomalyEvent` đã cập nhật (cùng shape với 1 item ở `GET /api/anomalies`, có thêm `reviewed_by` = id người vừa verify).
**401**: chưa đăng nhập. **403**: role không phải doctor/admin. **404**: không tìm thấy sự kiện. **422**: thiếu/sai `corrected_label`.

Mỗi lần verify **thành công** ghi 1 dòng vào bảng `audit_trails` (ai, lúc nào, kết quả gì) — verify lại 1 sự kiện đã verify trước đó vẫn được phép (ghi đè trạng thái mới nhất), lịch sử cũ không mất.

---

## Công cụ kiểm thử API thủ công

```bash
python -m backend.scripts.test_ws [record_id] [số_gói_tin]           # xem thử payload WS
python -m backend.scripts.seed_users                                  # tạo 3 tài khoản test
python -m backend.scripts.validate_auth                               # 18 assertion auth
python -m backend.scripts.validate_anomalies                          # 25 assertion anomalies + WS
python -m backend.scripts.validate_review                             # 16 assertion human-in-the-loop
```
