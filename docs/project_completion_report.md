# Báo Cáo Tổng Hợp Dự Án — ECG Arrhythmia Detection & Explainable AI

**Nhóm thực hiện**: Nguyễn Đào Nam Hải · Phan Thị Hải Yến
**Cập nhật**: 2026-09-21

Tài liệu này đối chiếu lại toàn bộ hệ thống đã xây dựng với **Project Definition** gốc, tổng
hợp kết quả đạt được ở từng phần (Dữ liệu/AI, Backend, Frontend, Bảo mật, Kiểm thử, Triển khai),
và nêu rõ những điểm lệch có chủ đích so với đề cương kèm lý do — dùng để báo cáo với thầy.

**Tài liệu chi tiết đi kèm** (không lặp lại nội dung ở đây, chỉ dẫn link):
- [ai_process_summary.md](ai_process_summary.md) — toàn bộ quá trình AI/ML (dữ liệu → benchmark → validation → generalization → fine-tune)
- [ai_results_gallery.md](ai_results_gallery.md) / [ai_overview.ipynb](ai_overview.ipynb) — hình ảnh/biểu đồ kết quả AI
- [architecture.md](architecture.md) — kiến trúc hệ thống chi tiết
- [api_reference.md](api_reference.md) — toàn bộ endpoint REST + WebSocket
- [deployment_guide.md](deployment_guide.md) — hướng dẫn triển khai Docker/thủ công
- [benchmark_results.md](benchmark_results.md) — số liệu benchmark đầy đủ (model, latency, throughput, AFib, generalization)
- [onnx_comparison.md](onnx_comparison.md) — so sánh PyTorch/ONNX FP32/ONNX INT8

---

## 1. Mục tiêu dự án

Xây dựng hệ thống giám sát điện tâm đồ (ECG) **thời gian thực**, dùng Deep Learning để **phát
hiện rối loạn nhịp tim** theo 5 lớp chuẩn AAMI (N/S/V/F/Q) và sàng lọc thêm Rung nhĩ (AFib),
kèm **Explainable AI (XAI)** giúp bác sĩ hiểu vì sao AI đưa ra cảnh báo — không phải hộp đen.
Hệ thống hướng tới hỗ trợ bác sĩ **chủ động theo dõi và sàng lọc sớm**, không thay thế chẩn
đoán lâm sàng đầy đủ.

---

## 2. Kiến trúc tổng quan

```
data/         Tiền xử lý MIT-BIH (Kaggle CSV + PhysioNet WFDB), SMOTE, xuất .npy
src/          5 kiến trúc model 1D (ResNet1D, CNN-LSTM, TCN, Transformer1D, Mamba1D) + Grad-CAM
backend/      FastAPI + WebSocket streaming, inference singleton, DSP, Auth, Database, REST API
frontend/     React 19 + Vite + Plotly — dashboard real-time, quản lý bệnh nhân, XAI, báo cáo
saved_models/ Trọng số model đã train (.pth, không commit git)
```

Client-Server, giao tiếp real-time qua **WebSocket** (độ trễ thấp là yêu cầu cốt lõi), REST API
cho các thao tác không cần streaming (auth, hồ sơ bệnh nhân, tra cứu lịch sử, upload chẩn đoán
offline). Chi tiết đầy đủ: [architecture.md](architecture.md).

---

## 3. Dữ liệu & Trí tuệ nhân tạo (AI/ML)

Đã có báo cáo riêng đầy đủ tại [ai_process_summary.md](ai_process_summary.md) — dưới đây chỉ
tóm tắt các mốc kết quả chính:

| Hạng mục | Kết quả |
|---|---|
| Benchmark 5 kiến trúc, chọn triển khai | **ResNet1D** — Accuracy 98.57%, F1-macro 92.16%, Latency 0.13ms/nhịp (cao/thấp nhất trong 5) |
| Sửa lỗi rò rỉ dữ liệu Validation | Val (98.62%) ≈ Test (98.51%), chênh 0.11 điểm % — hết overfit |
| Đánh giá end-to-end trên dữ liệu PhysioNet thật | Accuracy 96.62% (8 bản ghi, 20.546 nhịp, so nhãn bác sĩ) |
| Phát hiện đỉnh R (Pan-Tompkins) | F1 97.14% (so nhãn bác sĩ, 8 bản ghi) |
| Explainable AI | Grad-CAM 1D — khoanh vùng tín hiệu gây quyết định cho mọi nhịp bất thường |
| Xuất mô hình nhẹ (ONNX) | ONNX INT8: 697.3KB (đạt mục tiêu <700KB), Accuracy 93.66% (rớt <2 điểm % so gốc) |
| Sàng lọc Rung nhĩ (AFib) | Tầng rule-based riêng (`AfibScreener`) — **ngưỡng chưa kiểm chứng thống kê đầy đủ**, ghi rõ là nợ kỹ thuật |
| Generalization ngoài MIT-BIH | Lớp N/V ổn định 78-96% trên INCART/SVDB/EDB; lớp S/F **chưa** generalize tốt — đã thử fine-tune, ghi nhận trung thực giới hạn |
| Fine-tune INCART (đã lên production) | Accuracy INCART 85.94% → **93.18%**, không tụt 4 chỉ tiêu đề cương trên MIT-BIH |

---

## 4. Backend (FastAPI + PyTorch)

- **Xử lý tín hiệu**: bandpass (0.5-45Hz) + notch (50Hz) filter, chuẩn hoá biên độ, Pan-Tompkins
  R-peak detection động (`backend/core/`).
- **Inference singleton** (`ECGInferenceService`): nạp model 1 lần khi khởi động, trả về
  (nhãn, heatmap Grad-CAM, latency, confidence — xác suất softmax) cho mỗi nhịp.
- **WebSocket streaming** (`/ws/ecg`): stream tín hiệu 360Hz, 2 kênh (kênh chẩn đoán chính +
  kênh tham khảo), 36 gói/giây, tích hợp AfibScreener song song HRVTracker.
- **Database & ORM** (SQLAlchemy 2.0 + Alembic): 5 bảng (`users`, `patients`, `ecg_records`,
  `anomaly_events`, `audit_trails`), SQLite (đổi PostgreSQL được qua biến môi trường).
- **Authentication & Authorization**: JWT qua HttpOnly Secure cookie, 3 vai trò (admin/doctor/
  nurse) với phân quyền RBAC — vd nurse không được duyệt/sửa nhãn chẩn đoán.
- **Human-in-the-loop**: `POST /api/anomalies/{id}/verify` — bác sĩ duyệt hoặc sửa nhãn AI, mọi
  thao tác ghi vào `audit_trails` (truy vết trách nhiệm).
- **REST API đầy đủ**: auth, records, upload chẩn đoán offline (CSV), tra cứu lịch sử bất
  thường có lọc/phân trang — danh sách đầy đủ tại [api_reference.md](api_reference.md).

---

## 5. Frontend (React 19 + Vite + Plotly)

- **Dashboard giám sát real-time**: biểu đồ ECG 2 kênh (đã tự động co giãn trục y riêng từng
  kênh theo đúng biên độ thật), thẻ chỉ số (nhịp tim, HRV, độ tin cậy AI, chẩn đoán), badge
  cảnh báo đa tầng.
- **Hệ thống cảnh báo đa tầng** (🟢🟡🔴): âm thanh, tắt tiếng tạm thời (mute 2 phút, tự bật
  lại theo chuẩn IEC 60601-1-8), push notification.
- **Quản lý bệnh nhân**: hồ sơ bệnh nhân, chọn bản ghi đang stream, lưu trạng thái qua
  `localStorage` (chống mất dữ liệu khi F5).
- **Explainable AI UI**: trang Phân Tích XAI Chuyên Sâu — Grad-CAM heatmap phóng to, lịch sử
  cảnh báo, giải thích lâm sàng theo nhãn AAMI (không phơi thuật ngữ kỹ thuật thô cho bác sĩ).
- **Xuất báo cáo y tế**: PDF/CSV từ lịch sử cảnh báo.
- **Chẩn đoán offline**: upload file CSV, chạy full pipeline (lọc → R-peak → AI) trả kết quả.
- **Settings & Calibration** (admin-only): ngưỡng nhạy AI (`confidence` threshold).
- **Resilience**: tự động kết nối lại WebSocket sau 3 giây nếu rớt mạng, loading state rõ ràng.
- **Tách bạch thông tin lâm sàng vs kỹ thuật**: đã rà soát và ẩn/gom các chỉ số kỹ thuật thuần
  (mã AAMI, latency số nguyên) khỏi luồng thông tin chính bác sĩ nhìn thấy, chỉ giữ ngôn ngữ
  lâm sàng ở giao diện chính.

---

## 6. Kiểm thử & Chất lượng (Testing/QA)

| Hạng mục | Trạng thái |
|---|---|
| Backend test suite (`pytest`) | **42/42 xanh** (auth, records, WS, anomalies, human-in-the-loop, DB) |
| Frontend test (`Vitest`) | Có (ReportExporter), chưa phủ hết mọi component |
| Lint backend | `ruff check` — sạch |
| Lint frontend | `oxlint` — sạch |
| CI/CD (`GitHub Actions`) | 5 job: lint-backend, lint-frontend, test-backend, test-frontend, build-docker — chạy tự động mọi PR/push vào `main` |

---

## 7. Hạ tầng & Triển khai (tóm tắt — chi tiết xem `deployment_guide.md`)

- **Docker Compose**: 2 container (backend FastAPI + frontend Nginx phục vụ file tĩnh React đã
  build), reverse proxy `/api`, `/ws` qua Nginx.
- **CI/CD**: tự động lint + test + build Docker + smoke test trên mọi thay đổi.
- **Đa máy truy cập (LAN)**: frontend gọi API/WS bằng đường dẫn tương đối, tự khớp origin —
  bất kỳ máy nào trong LAN mở đúng địa chỉ máy chủ là dùng được, không cần cấu hình lại.
- Phần triển khai công khai qua Internet (nếu có) và chi tiết hạ tầng nằm ngoài phạm vi báo cáo
  AI/hệ thống này — xem `deployment_guide.md`.

---

## 8. Đối chiếu tiến độ theo Checkpoint

| Checkpoint | Hạng mục | Trạng thái |
|:---|:---|:---:|
| CP 1 | Tiền xử lý MIT-BIH, SMOTE, 5 model, Benchmark, Grad-CAM | ✅ 100% |
| CP 2 | FastAPI WebSocket, Inference singleton, Dashboard, XAI Page | ✅ 100% |
| CP 3 | DSP, Pan-Tompkins R-peak, BPM/HRV, record switcher, upload chẩn đoán | ✅ 100% |
| CP 4 | Patient Management, Alarm System, Report Exporter, XAI Explainer, Settings | ✅ 100% |
| CP 5 | Database, Auth JWT, RBAC, Human-in-the-loop | ✅ 100% |
| CP 6 | ONNX, Test Suite, Docker, CI/CD, Docs | ✅ 100% |
| Việc bổ sung khớp đề cương | AFib screening, Validation split, đo E2E Latency, đo Throughput | ✅ 100% (AFib screening còn nợ kỹ thuật về ngưỡng, đã ghi rõ) |

---

## 9. Các điểm lệch có chủ đích so với Project Definition gốc (kèm lý do)

| Đề cương gốc | Đã triển khai | Lý do |
|---|---|---|
| TensorFlow | **PyTorch** | Cần autograd 2 chiều cho Grad-CAM (backward pass); API linh hoạt hơn cho kiến trúc tuỳ biến (ResNet1D, Transformer1D, Mamba1D); hệ sinh thái ONNX export tốt hơn cho tối ưu triển khai |
| Streamlit | **React + Vite + Plotly + WebSocket** | Streamlit rerun toàn trang mỗi lần cập nhật — không phù hợp luồng real-time 36 gói/giây độ trễ thấp mà chính đề cương yêu cầu; đổi công nghệ để phục vụ TỐT HƠN mục tiêu latency đã cam kết |
| 3 lớp rối loạn nhịp | **5 lớp chuẩn AAMI** (N/S/V/F/Q) + tầng AFib riêng | AAMI 5 lớp là chuẩn quốc tế phổ biến hơn cho phân loại từng nhịp, bao phủ rộng hơn 3 nhóm gốc; Rung nhĩ (chẩn đoán theo nhịp điệu kéo dài) tách thành tầng rule-based riêng vì khác bản chất bài toán so với phân loại hình dạng từng nhịp |

---

## 10. Giới hạn đã biết (nói thật, không tô hồng)

- **Ngưỡng AFib (0.62)** chọn tay theo trực giác, chưa kiểm chứng thống kê đầy đủ do hạn chế
  tải dữ liệu AFDB trong quá trình làm — coi là gợi ý sàng lọc, không phải kết luận chẩn đoán.
- **Lớp S (Trên thất) và F (Hợp nhất)** chưa generalize tốt ngoài MIT-BIH (SVDB Recall_S 0.4%,
  EDB 3.6%) — đã thử 2 kỹ thuật fine-tune, đều thất bại vì giới hạn hình học bài toán 5 lớp
  dùng chung 1 mặt quyết định; sửa triệt để cần train lại từ đầu với dữ liệu đa nguồn.
- **Phạm vi thiết bị an toàn**: hệ thống đáng tin nhất với thiết bị Holter/đạo trình kiểu MLII
  giống MIT-BIH — đổi sang thiết bị khác cần fine-tune lại trước khi triển khai.
- **Throughput**: benchmark local cho thấy ổn định tới ~10 kết nối đồng thời/1 node backend —
  cần đo lại trên hạ tầng deployment thật trước khi công bố ngưỡng production.
- Hệ thống là **công cụ sàng lọc hỗ trợ**, không thay thế ECG 12 chuyển đạo chẩn đoán đầy đủ hay
  quyết định lâm sàng của bác sĩ.

---

## 11. Kết luận

Hệ thống đã hoàn thành đầy đủ 6 checkpoint chính theo đề cương (CP1-CP6) cộng 4 hạng mục bổ
sung để khớp sát Project Definition (AFib screening, Validation split đúng chuẩn, đo End-to-End
Latency, đo Throughput). Model AI đã được benchmark khách quan qua 5 kiến trúc, kiểm chứng
không overfit, đánh giá trên dữ liệu PhysioNet thật và trên 3 bộ dữ liệu độc lập ngoài MIT-BIH —
mọi kết quả đều được đo và ghi nhận trung thực, bao gồm cả các giới hạn chưa giải quyết được.
Hệ thống đã sẵn sàng dùng làm công cụ sàng lọc hỗ trợ bác sĩ trong phạm vi thiết bị Holter/MLII
tương tự MIT-BIH, với các hướng phát triển tiếp theo đã được xác định rõ (train đa nguồn cho lớp
S/F, hiệu chỉnh đầy đủ ngưỡng AFib bằng bộ AFDB đầy đủ).
