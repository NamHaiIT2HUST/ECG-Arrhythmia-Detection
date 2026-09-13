# KẾ HOẠCH HOÀN THIỆN — KHỚP ĐÚNG ĐỀ CƯƠNG DỰ ÁN

> **Mục đích**: đóng đúng 4 khoảng lệch thật (có thể đo/code được) giữa đề cương gốc và hệ thống hiện tại (đã audit chi tiết ở cuộc trò chuyện trước). 2 khoảng lệch còn lại (đổi TensorFlow→PyTorch, đổi Streamlit→React) **không phải việc code** — chỉ cần viết giải trình trong báo cáo cuối, xem mục 5.
> **Không phá vỡ gì đang chạy**: cả 4 việc dưới đây đều là **thêm mới** (module mới, script đo mới) hoặc **retrain có kiểm soát** (không đụng vào pipeline serving đã validate 94.33% end-to-end) — rủi ro hồi quy thấp.

---

## 0. TÓM TẮT 4 VIỆC CẦN LÀM

| # | Khoảng lệch trong đề cương | Việc cần làm | Độ khó |
|---|---|---|---|
| 1 | "Rung nhĩ" là 1 trong 3 lớp mục tiêu, nhưng hệ thống hiện không phát hiện Rung nhĩ (chỉ phân loại AAMI 5 lớp theo từng nhịp) | Xây module **screening Rung nhĩ theo nhịp điệu** (rhythm-level), tận dụng `HRVTracker` đã có sẵn | Trung bình |
| 2 | "Chia Train/Validation/Test" nhưng thực tế chỉ có Train/Test | Thêm tập Validation, theo dõi val loss/accuracy khi train lại model production (ResNet1D) | Thấp |
| 3 | Cam kết "End-to-End Latency < 2 giây" nhưng chưa từng đo con số này | Viết script đo latency thật, từ lúc phát hiện nhịp tới lúc gửi kết quả qua WS | Thấp |
| 4 | Đề cương liệt kê "Throughput" là 1 chỉ số cần đánh giá nhưng chưa từng đo | Viết script benchmark nhiều kết nối WS đồng thời, đo nhịp/giây hệ thống xử lý được | Thấp-Trung bình |

---

## 1. XÂY MODULE SCREENING RUNG NHĨ (ATRIAL FIBRILLATION)

### 1.1. Vì sao không thể chỉ "thêm 1 lớp" vào model 5 lớp hiện có

Rung nhĩ (AFib) là chẩn đoán **theo nhịp điệu kéo dài** (RR không đều "irregularly irregular" + mất sóng P qua nhiều nhịp liên tiếp), khác về bản chất với phân loại **hình dạng từng nhịp đơn lẻ** mà model ResNet1D/CNN1D-LSTM đang làm (mỗi lần chỉ nhìn 1 cửa sổ 187 điểm quanh 1 đỉnh R). Không thể thêm "lớp Rung nhĩ" vào bài toán phân loại nhịp đơn lẻ hiện có — cần 1 tầng phân tích **riêng, nhìn theo chuỗi nhiều nhịp**.

**Cũng không dùng được đúng bộ dữ liệu hiện có (`data/raw/physionet_mitdb/`)**: MIT-BIH Arrhythmia Database dùng để train hiện tại không có đủ nhãn Rung nhĩ kéo dài đại diện. Cần dùng **MIT-BIH Atrial Fibrillation Database (AFDB)** — 1 bộ dữ liệu RIÊNG trên PhysioNet, có nhãn nhịp điệu (`rhythm annotation`, ký hiệu `(AFIB`, `(N`...) theo từng đoạn, khác hẳn nhãn từng nhịp `.atr` đang dùng.

### 1.2. Cách làm — khuyến nghị: dùng đặc trưng RR-interval kinh điển, KHÔNG cần train model DL mới

Vì đã có sẵn `HRVTracker` (theo dõi cửa sổ trượt tối đa 50 khoảng RR/kết nối, xem `backend/core/hrv.py`), cách nhanh và đủ tin cậy nhất là tính thêm vài đặc trưng đo độ bất thường (irregularity) đã được y văn chứng minh hiệu quả cho sàng lọc AFib, KHÔNG cần train lại mạng nơ-ron mới:

- **pNN50**: % số cặp khoảng RR liên tiếp lệch nhau > 50ms — AFib có tỉ lệ này rất cao do nhịp hỗn loạn.
- **Hệ số biến thiên RR** (SDNN / mean RR): AFib có biến thiên RR lớn bất thường, không theo mẫu hình sin đều như nhịp xoang.
- **Tỉ lệ SD1/SD2 (Poincaré plot)**: AFib có hình quạt phân tán đặc trưng, tỉ lệ SD1/SD2 cao hơn hẳn nhịp bình thường.

Đặt ngưỡng (threshold) cho tổ hợp 3 đặc trưng trên qua thực nghiệm — đây là cách tiếp cận **rule-based/thống kê cổ điển**, chấp nhận được và phổ biến trong sàng lọc AFib lâm sàng thực tế (không phải "làm tắt", nhiều thiết bị AliveCor/Apple Watch cũng dùng phương pháp tương tự cho tầng sàng lọc đầu).

**Nếu còn thời gian, làm thêm (không bắt buộc)**: thay ngưỡng cố định bằng 1 model nhỏ (Logistic Regression / MLP nông) train trên đúng 3 đặc trưng trên, dùng nhãn thật từ AFDB — nâng cấp từ "rule-based" lên "có học máy" mà không cần đổi kiến trúc lớn.

### 1.3. File cần tạo/sửa

- **`backend/core/afib_screener.py`** (mới) — class `AfibScreener`, cùng pattern với `HRVTracker`:
  ```python
  class AfibScreener:
      def __init__(self, max_history=50): ...
      def update(self, rr_ms_history) -> {"afib_suspected": bool, "afib_score": float}
  ```
- **`backend/scripts/download_afdb_sample.py`** (mới, tuỳ chọn) — script tải vài bản ghi từ MIT-BIH AFDB (dùng `wfdb.dl_database('afdb', ...)`, thư viện `wfdb` đã có sẵn trong `requirements.txt`) để có dữ liệu đánh giá/hiệu chỉnh ngưỡng.
- **`backend/scripts/calibrate_afib_thresholds.py`** (mới) — chạy qua các bản ghi AFDB đã tải, tính 3 đặc trưng trên cho từng đoạn có nhãn AFIB/không AFIB, tìm ngưỡng tối ưu (vd bằng ROC curve), in ra Sensitivity/Specificity.
- **Tích hợp**: `backend/api/ws_routes.py` — gọi `AfibScreener.update()` cùng lúc với `HRVTracker.update()` (đã có sẵn `hrv_sdnn` trong lịch sử để tái sử dụng), thêm field tuỳ chọn `"afib_suspected": bool` vào payload WS (không phá schema cũ).
- **Frontend (nhỏ, tuỳ chọn)**: `StatCards.jsx` hoặc `Header.jsx` thêm 1 badge cảnh báo "⚠️ Nghi ngờ Rung Nhĩ" khi `afib_suspected=true`.

### 1.4. DoD

- [ ] `calibrate_afib_thresholds.py` chạy ra được Sensitivity/Specificity trên tập AFDB đã tải, ghi vào `docs/benchmark_results.md` mục mới "AFib Screening".
- [ ] WS payload có field `afib_suspected`, kiểm chứng bằng `backend/scripts/test_ws.py` hiện có.
- [ ] Cập nhật `plan.md`/báo cáo: hệ thống giờ có 2 tầng phân tích — (a) phân loại AAMI 5 lớp theo từng nhịp (deep learning), (b) sàng lọc Rung nhĩ theo nhịp điệu (rule-based trên đặc trưng RR) — đúng tinh thần đề cương, giải thích rõ vì sao 2 bài toán cần 2 phương pháp khác nhau.

---

## 2. THÊM TẬP VALIDATION KHI TRAIN

### 2.1. Hiện trạng

`src/benchmark.py::train_and_eval_model(model_name, model, train_loader, test_loader, ...)` — chỉ nhận `train_loader`/`test_loader`, train cố định 10 epoch không theo dõi validation, không early-stopping.

### 2.2. Cách làm

- Sửa `load_data()` ([src/benchmark.py:26](src/benchmark.py#L26)): sau khi nạp `X_train`/`y_train`, tách thêm 10% làm validation bằng `train_test_split(..., stratify=y_train, random_state=42)` (giữ đúng tinh thần "chia tách trước khi cân bằng" đã áp dụng nhất quán trong dự án — xem `plan.md` mục 1.2).
- Sửa `train_and_eval_model()`: sau mỗi epoch, chạy `model.eval()` trên `val_loader`, tính val loss + val accuracy, in ra cùng dòng log epoch hiện có.
- **Không bắt buộc phải retrain cả 5 model** — chỉ cần retrain lại đúng **ResNet1D (model production)** với quy trình Train/Val/Test đầy đủ, ghi rõ trong báo cáo: *"4 model còn lại dùng Train/Test cho vòng khảo sát kiến trúc (architecture screening); model được chọn triển khai (ResNet1D) được huấn luyện lại đầy đủ với Train/Validation/Test"* — đây là lý do phương pháp luận hợp lý, không phải chống chế.
- (Tuỳ chọn, nếu val loss có dấu hiệu overfit rõ ở epoch cuối) thêm early-stopping đơn giản: dừng nếu val loss không giảm sau 2 epoch liên tiếp.

### 2.3. File cần sửa

- `src/benchmark.py`: `load_data()`, `train_and_eval_model()`.
- `docs/benchmark_results.md`: thêm cột/mục val accuracy + val loss cho ResNet1D.

### 2.4. DoD

- [ ] Chạy `python src/benchmark.py --model resnet1d` (hoặc tương đương) ra log có dòng val loss/accuracy mỗi epoch.
- [ ] Test accuracy cuối cùng của ResNet1D không đổi nhiều so với số đã có (98.57%) — nếu lệch nhiều cần kiểm tra lại (dấu hiệu leak dữ liệu hoặc tách sai).
- [ ] `saved_models/resnet1d.pth` được ghi đè bằng bản train lại — **chạy lại toàn bộ `pytest` + `validate_classification.py` sau khi thay file này** để đảm bảo không hồi quy pipeline serving.

---

## 3. ĐO END-TO-END LATENCY

### 3.1. Định nghĩa đo (cần nói rõ trong báo cáo)

"End-to-End Latency" ở đây đo từ **lúc 1 đỉnh R được phát hiện trong luồng dữ liệu** (`data_streamer.py`) đến **lúc payload JSON tương ứng được gửi qua WebSocket** (`websocket.send_json()` trong `ws_routes.py`) — đây là phần **backend thật sự kiểm soát và đo được đáng tin cậy**. Độ trễ mạng + render frontend (phụ thuộc trình duyệt/mạng người dùng, không phải lỗi hệ thống) sẽ nêu là giới hạn đo, không gộp vào con số chính.

### 3.2. Cách làm

- Thêm 1 script mới: **`backend/scripts/benchmark_e2e_latency.py`** — mở 1 kết nối WS thật tới `/ws/ecg` (dùng `TestClient` hoặc thư viện `websockets`), lắng nghe N gói tin có `is_new_beat=true`, đo khoảng cách thời gian giữa 2 lần `is_new_beat=true` liên tiếp so với thời điểm gói tin đó THỰC SỰ được gửi (cần thêm 1 timestamp nội bộ trong `ws_routes.py` ngay trước `await websocket.send_json(payload)`, so với timestamp lúc `beat_info` được tạo ra trong `data_streamer.py` — chênh lệch 2 mốc này chính là latency cần đo).
- Chạy trên vài bản ghi khác nhau (100, 208, 234...), báo cáo **trung bình, p95, max** (không chỉ trung bình — trung bình có thể che giấu vài lần trễ đột biến).

### 3.3. DoD

- [ ] Script chạy ra bảng số liệu latency (ms) — kỳ vọng vài chục ms, dư sức dưới ngưỡng 2000ms đề cương yêu cầu.
- [ ] Ghi số liệu vào `docs/benchmark_results.md` mục mới "End-to-End Latency".

---

## 4. ĐO THROUGHPUT

### 4.1. Cách làm

- Thêm script mới: **`backend/scripts/benchmark_throughput.py`** — dùng thư viện `websockets` (async) mở **K kết nối WS đồng thời** (mô phỏng K bệnh nhân/giường theo dõi cùng lúc, đúng kịch bản CP4.1 multi-bed monitoring), mỗi kết nối stream 1 bản ghi khác nhau trong `data/raw/physionet_mitdb/`.
- Tăng dần K (vd 1, 5, 10, 20...), với mỗi mức đo: (a) tổng số nhịp toàn hệ thống xử lý được/giây, (b) latency trung bình per-connection có bị tăng lên không (dấu hiệu quá tải).
- Báo cáo: **"Hệ thống chịu được ổn định tối đa K bệnh nhân đồng thời trên 1 máy [cấu hình CPU cụ thể], tổng Y nhịp/giây, latency không tăng đáng kể tới ngưỡng đó."**

### 4.2. DoD

- [ ] Script chạy ra bảng K vs (throughput, latency trung bình).
- [ ] Ghi số liệu + khuyến nghị giới hạn triển khai thực tế vào `docs/benchmark_results.md`.

---

## 5. VIỆC KHÔNG PHẢI CODE — CHỈ CẦN VIẾT VÀO BÁO CÁO CUỐI

- **TensorFlow → PyTorch**: giải trình ngắn — PyTorch cho phép autograd 2 chiều cần thiết cho Grad-CAM (backward pass), API linh hoạt hơn cho kiến trúc tuỳ biến (ResNet1D, Transformer1D, Mamba1D), hệ sinh thái ONNX export tốt hơn cho tối ưu triển khai (đã làm ở CP6.1).
- **Streamlit → React + Plotly + WebSocket**: giải trình ngắn — Streamlit dùng mô hình "rerun toàn trang" mỗi lần tương tác/refresh, không phù hợp cập nhật liên tục ~36 lần/giây qua WebSocket với độ trễ thấp; React với state cục bộ + WebSocket client cho phép cập nhật mượt, đúng yêu cầu latency thấp mà chính đề cương đặt ra — tức là đổi công nghệ CHÍNH LÀ để phục vụ tốt hơn mục tiêu latency đã cam kết, không phải đi lệch mục tiêu.
- **3 lớp → 5 lớp AAMI**: giải trình — chuẩn AAMI 5 lớp là chuẩn quốc tế phổ biến hơn cho bài toán phân loại nhịp tim đơn lẻ (không phải tự đặt ra), bao phủ rộng hơn 3 nhóm đề cương ban đầu, Rung nhĩ được xử lý bằng tầng riêng (mục 1) đúng bản chất bài toán khác của nó.

---

## 6. THỨ TỰ LÀM ĐỀ XUẤT

1. Mục 3 (đo E2E latency) + Mục 4 (đo throughput) — làm trước, nhanh, không đụng gì tới model/dữ liệu train, rủi ro bằng 0.
2. Mục 2 (Validation split + retrain ResNet1D) — làm tiếp, có kiểm soát, nhớ chạy lại toàn bộ `pytest`/`validate_classification.py` sau khi thay `saved_models/resnet1d.pth`.
3. Mục 1 (AFib screening) — việc lớn nhất, làm sau cùng khi đã chắc các phần khác ổn, vì cần tải thêm dữ liệu AFDB mới (ngoài `data/raw/physionet_mitdb/` hiện có).
