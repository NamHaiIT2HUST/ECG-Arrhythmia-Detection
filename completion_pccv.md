# PHÂN CÔNG CÔNG VIỆC — HOÀN THIỆN 4 VIỆC CÒN LẠI (theo `completion_plan.md`)

> Tài liệu này chia 4 việc trong [completion_plan.md](completion_plan.md) cho 2 người, ưu tiên tối đa tính độc lập (ít đụng chung file nhất có thể). Theo đúng format/nguyên tắc đã dùng ở [pccv.md](pccv.md) gốc — mỗi việc nhỏ 1 nhánh riêng, PR nhỏ, sync qua báo trong nhóm chat, không họp.
> **Điền tên trước khi bắt đầu**:
> - **NGƯỜI 1**: `____________` (đề xuất: NamHaiIT2HUST, tiếp tục quen việc benchmark/backend)
> - **NGƯỜI 2**: `____________` (đề xuất: yenpth265-alt)
>
> Đề xuất ở trên chỉ là gợi ý cân bằng khối lượng việc — 2 người có thể tự đổi cho nhau, không ảnh hưởng cấu trúc phân công.

---

## 0. NGUYÊN TẮC CHUNG (giữ nguyên như `pccv.md` gốc)

1. Mỗi việc nhỏ (C1-C4) = 1 nhánh riêng `feat/<tên-việc>`, tách từ `main` mới nhất, PR riêng, merge xong báo trong nhóm chat.
2. Trước khi bắt đầu: `git checkout main && git pull` để chắc chắn tách từ bản mới nhất.
3. **Có đúng 1 điểm giao nhau giữa 2 người** (xem mục 3) — không có điểm nào khác, đọc kỹ mục 3 trước khi làm `ws_routes.py`.
4. Không sửa file thuộc việc của người kia ngoài đúng điểm giao đã ghi rõ ở mục 3.

---

## 1. TỔNG QUAN PHÂN CÔNG

| | Người 1 | Người 2 |
|---|---|---|
| Việc nhỏ | **C1**. Đo E2E Latency<br>**C2**. Validation split + retrain ResNet1D | **C3**. Đo Throughput<br>**C4**. Sàng lọc Rung nhĩ (AFib) |
| File chính đụng tới | `src/benchmark.py`, `backend/scripts/benchmark_e2e_latency.py` (mới), `backend/service/data_streamer.py` (1 dòng) | `backend/scripts/benchmark_throughput.py` (mới, hoàn toàn độc lập), `backend/core/afib_screener.py` (mới) |
| Điểm giao duy nhất | `backend/api/ws_routes.py` — cả 2 đều thêm **1 field mới** vào payload WS (xem mục 3) |
| Khối lượng | 1 việc nhỏ (C1) + 1 việc vừa (C2, có retrain) | 1 việc rất nhỏ, độc lập hoàn toàn (C3) + 1 việc lớn nhất (C4) |

**Vì sao chia thế này**: C3 (throughput) hoàn toàn không đụng code production (chỉ mở kết nối WS từ bên ngoài để đo) — cho Người 2 làm trước để khởi động, không phải chờ ai. C1 và C2 đều xoay quanh benchmark/training (`src/benchmark.py`, `docs/benchmark_results.md`) nên gộp cho 1 người làm liền mạch, đỡ phải đọc lại context. C4 (AFib) là việc lớn nhất, tận dụng đúng thời gian Người 2 đã "khởi động" xong C3.

---

## 2. NGƯỜI 1 — C1 + C2

### C1. Đo End-to-End Latency

- **Chi tiết đầy đủ**: `completion_plan.md` mục 3.
- **Không phụ thuộc ai, làm trước tiên** — nhanh nhất trong 4 việc.
- **Việc cụ thể**:
  1. `backend/service/data_streamer.py`: trong `ecg_file_reader()`, ngay lúc tạo `beat_info` (khi phát hiện 1 đỉnh R mới), thêm 1 key `"detected_at": time.time()` vào dict `beat_info` — **chỉ thêm 1 dòng**, không đổi gì khác trong hàm.
  2. `backend/api/ws_routes.py`: ngay trước `await websocket.send_json(payload)`, tính `latency_e2e_ms = (time.time() - beat_info["detected_at"]) * 1000` nếu `beat_info is not None`, thêm field `"latency_e2e_ms"` vào `payload` — **đây là điểm giao với Người 2, xem mục 3 trước khi sửa**.
  3. Viết `backend/scripts/benchmark_e2e_latency.py`: mở WS thật tới `/ws/ecg`, lắng nghe N gói có `is_new_beat=true`, gom lại `latency_e2e_ms`, in bảng trung bình/p95/max cho vài bản ghi (100, 208, 234).
- **✅ Khi xong, báo**: "C1 xong — latency_e2e trung bình X ms, p95 Y ms, PR #___".
- **DoD**: script chạy ra số liệu, ghi vào `docs/benchmark_results.md` mục "End-to-End Latency" (mục mới, không đụng nội dung cũ trong file).

### C2. Thêm Validation split + retrain ResNet1D

- **Chi tiết đầy đủ**: `completion_plan.md` mục 2.
- **Phụ thuộc**: không phụ thuộc C1, nhưng nên làm sau C1 (cùng đụng `docs/benchmark_results.md`, làm liền mạch đỡ conflict với chính mình).
- **Việc cụ thể**:
  1. `src/benchmark.py::load_data()`: tách thêm validation set từ `X_train`/`y_train` (`train_test_split(..., stratify=y_train, test_size=0.1, random_state=42)`).
  2. `src/benchmark.py::train_and_eval_model()`: thêm tham số `val_loader`, sau mỗi epoch chạy eval trên validation, in val loss + val accuracy.
  3. Chạy retrain **chỉ ResNet1D** (không cần chạy lại 4 model kia): `python src/benchmark.py --model resnet1d` (hoặc cách gọi tương ứng hiện có).
  4. Ghi đè `saved_models/resnet1d.pth` bằng bản mới.
  5. **Bắt buộc chạy lại để xác nhận không hồi quy**: `pytest tests/ -v` (26-28 test hiện có) + `python -m backend.scripts.validate_classification` (accuracy end-to-end phải vẫn ~94% như cũ, không được tụt nhiều).
- **✅ Khi xong, báo**: "C2 xong — ResNet1D retrain với Val, test accuracy X%, val accuracy Y%, validate_classification vẫn Z% (so với 94.33% cũ), PR #___".
- **DoD**: `pytest` xanh hết, `validate_classification.py` không tụt accuracy đáng kể, `docs/benchmark_results.md` có thêm cột val accuracy/val loss cho ResNet1D + 1 câu giải thích ngắn vì sao chỉ retrain 1/5 model (đã viết sẵn lý do ở `completion_plan.md` mục 2.2, copy vào).

---

## 3. NGƯỜI 2 — C3 + C4

### C3. Đo Throughput

- **Chi tiết đầy đủ**: `completion_plan.md` mục 4.
- **Không phụ thuộc ai, không đụng code production** — chạy `uvicorn backend.main:app` lên rồi viết script bên ngoài gọi vào, không sửa file nào trong `backend/` cả (trừ chính script mới). Làm trước tiên để khởi động, không phải chờ Người 1.
- **Việc cụ thể**:
  1. Viết `backend/scripts/benchmark_throughput.py`: dùng thư viện `websockets` (thêm vào `requirements.txt` nếu chưa có — kiểm tra trước, có thể `wfdb`/`fastapi` đã kéo theo sẵn) mở K kết nối đồng thời tới `/ws/ecg?record=<id>` (mỗi kết nối 1 bản ghi PhysioNet khác nhau trong 48 bản ghi có sẵn), chạy song song bằng `asyncio.gather`.
  2. Đo với K = 1, 5, 10, 20 (tăng dần), mỗi mức: tổng nhịp/giây toàn hệ thống, latency trung bình mỗi kết nối (dùng field `latency_ms` đã có sẵn trong payload — không cần chờ C1 xong, dùng field cũ trước cũng được, field mới của C1 chỉ để chính xác hơn).
  3. In bảng K vs (throughput, latency trung bình).
- **✅ Khi xong, báo**: "C3 xong — hệ thống ổn định tới K=__ kết nối đồng thời, throughput __ nhịp/giây, PR #___".
- **DoD**: script chạy ra bảng số liệu, ghi vào `docs/benchmark_results.md` mục "Throughput" (mục mới).

### C4. Sàng lọc Rung nhĩ (AFib)

- **Chi tiết đầy đủ**: `completion_plan.md` mục 1 — đọc kỹ mục 1.1 (vì sao không thể chỉ thêm 1 lớp vào model hiện có) trước khi làm, tránh hiểu nhầm hướng.
- **Không phụ thuộc C3** (có thể làm song song), nhưng nên làm sau C3 để quen nhịp trước khi vào việc lớn nhất.
- **Việc cụ thể** (theo đúng thứ tự để giảm rủi ro):
  1. `backend/scripts/download_afdb_sample.py`: tải vài bản ghi từ MIT-BIH Atrial Fibrillation Database (`wfdb.dl_database('afdb', dl_dir='data/raw/physionet_afdb', records=[...])`) — bộ dữ liệu RIÊNG, không phải `physionet_mitdb` hiện có.
  2. `backend/core/afib_screener.py`: class `AfibScreener`, cùng pattern `HRVTracker` (`backend/core/hrv.py`) — nhận vào lịch sử RR-interval (ms), tính pNN50 + hệ số biến thiên RR + SD1/SD2 Poincaré, trả về `{"afib_suspected": bool, "afib_score": float}`.
  3. `backend/scripts/calibrate_afib_thresholds.py`: chạy `AfibScreener` qua các bản ghi AFDB đã tải (có nhãn rhythm annotation `(AFIB`/`(N`), tìm ngưỡng tối ưu qua ROC, in Sensitivity/Specificity.
  4. Tích hợp `backend/api/ws_routes.py`: gọi `AfibScreener.update()` song song `HRVTracker.update()` (tái dùng `hrv_sdnn`/lịch sử RR đã có), thêm field `"afib_suspected"` vào payload — **điểm giao với Người 1, xem mục 4 trước khi sửa**.
  5. (Tuỳ chọn, nếu còn thời gian) `frontend/src/components/dashboard/StatCards.jsx` hoặc `Header.jsx`: thêm badge nhỏ "⚠️ Nghi ngờ Rung Nhĩ" khi `afib_suspected=true`.
- **✅ Khi xong, báo**: "C4 xong — AfibScreener đạt Sensitivity X%/Specificity Y% trên tập AFDB hiệu chỉnh, PR #___".
- **DoD**: `calibrate_afib_thresholds.py` chạy ra Sensitivity/Specificity ghi vào `docs/benchmark_results.md` mục "AFib Screening"; payload WS có field mới, kiểm chứng bằng `backend/scripts/test_ws.py`.

---

## 4. ĐIỂM GIAO DUY NHẤT — `backend/api/ws_routes.py`

Cả C1 (Người 1) và C4 (Người 2) đều cần thêm **đúng 1 field mới** vào cùng 1 dict `payload` trong `ws_routes.py` (`latency_e2e_ms` và `afib_suspected`). Đây là điểm chạm DUY NHẤT giữa 2 track.

**Cách xử lý không cần chờ nhau**:
- Ai xong trước thì merge PR trước, báo trong nhóm chat "đã thêm field `<tên field>` vào payload WS, PR #___ đã merge".
- Người còn lại: `git checkout main && git pull` trước khi mở PR của mình (hoặc nếu đã lỡ tách nhánh từ trước, `git merge main` vào nhánh đang làm) — vì chỉ thêm 1 dòng mới vào dict `payload`, gần như chắc chắn tự merge sạch không conflict; nếu có conflict thì chỉ là 2 dòng thêm liền kề nhau trong cùng dict, tự chọn giữ cả 2 dòng là xong, không cần đọc lại logic gì thêm.
- Không ai cần đợi ai để BẮT ĐẦU code — chỉ cần biết thứ tự merge lúc PUSH cuối cùng.

---

## 5. CHECKLIST TỔNG HỢP

**Người 1**
- [ ] C1 — Đo End-to-End Latency
- [ ] C2 — Validation split + retrain ResNet1D

**Người 2**
- [ ] C3 — Đo Throughput
- [ ] C4 — Sàng lọc Rung nhĩ (AFib)

**Chung (sau khi cả 2 xong)**
- [ ] Cập nhật `plan.md`/báo cáo cuối: đối chiếu lại đề cương gốc, xác nhận đã đóng đủ 4 khoảng lệch + viết phần giải trình 2 khoảng lệch còn lại (TensorFlow→PyTorch, Streamlit→React) theo đúng nội dung đã có sẵn ở `completion_plan.md` mục 5.
