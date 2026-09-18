# KẾ HOẠCH MỞ RỘNG NGHIÊN CỨU — TỪ ĐỒ ÁN SANG PAPER

> **Mục đích tài liệu này**: mô tả cụ thể cần thay đổi/xây thêm gì trên codebase hiện tại (đã hoàn thành CP1-CP6, xem [plan.md](plan.md)) để có 1 đóng góp đủ chất lượng viết paper — không phải thêm tính năng sản phẩm, mà là 1 thực nghiệm khoa học có thiết kế, có đo lường, có so sánh.
> **Không phải checkpoint bắt buộc** — đây là đề xuất, làm tới đâu tuỳ thời gian/mục tiêu (nộp hội nghị sinh viên, khoá luận, hay chỉ để có thêm 1 mục nổi bật trong báo cáo).
> **Căn cứ lựa chọn hướng đi**: xem mục 0 — đã khảo sát thị trường + literature 2025-2026 thật (không phải suy đoán), tránh chọn hướng đã quá đông người làm.

---

## 0. CĂN CỨ — VÌ SAO CHỌN 2 HƯỚNG NÀY

Đã khảo sát (tháng 9/2026) các hướng "nghiên cứu AI cho ECG" đang hot: adversarial robustness (đã đông — ECG-ATK-GAN 2021, CardioDefense 2022, Lipschitz+CAS 2024, thêm 1 paper 2/2025), TinyML/edge deployment (cực đông năm 2025-2026, đã có cả federated learning trên model <5KB), cá nhân hoá per-patient (đang dùng cả Mamba/state-space model, bar kỹ thuật lên rất nhanh), XAI faithfulness (đã có paper 2025 định lượng cụ thể % khớp với vùng bác sĩ nhìn). Những hướng này khó tạo khác biệt cho 1 nhóm nhỏ trong thời gian ngắn.

**Phát hiện then chốt**: 1 systematic review tháng 3/2025 ([arXiv 2503.07276](https://arxiv.org/abs/2503.07276)) phê bình thẳng vào ngành: *"nhiều nghiên cứu báo accuracy cao nhưng rất ít dùng đúng inter-patient split, và hầu như bỏ qua ràng buộc phần cứng/triển khai thật — những con số ấn tượng che giấu lỗi phương pháp luận cơ bản khiến không dùng được thực tế"*. Dự án này đã **trải qua đúng chuyện đó thật** (không phải giả định): benchmark offline 98.57%, nhưng serving trên tín hiệu PhysioNet thô ban đầu chỉ đạt **0.2%** accuracy, sau vài lần vá tăng dần 22.9%, cuối cùng mới đạt lại 94.33% sau khi tìm đúng gốc rễ (lệch miền dữ liệu, lỗi resample từng nhịp — xem `plan.md` mục 3.0-3.1). Đây là chất liệu case-study hiếm có, đã có sẵn số liệu, đúng lúc ngành đang thiếu.

**2 hướng đề xuất** (độc lập, có thể làm 1 hoặc cả 2):
- **Hướng A (chính, khuyến nghị)**: biến case-study có sẵn thành 1 công cụ tái sử dụng được — bộ giám sát lệch miền dữ liệu (domain-shift detector) chạy runtime.
- **Hướng B (phụ, có thể làm song song)**: conformal prediction để ưu tiên hàng đợi bác sĩ duyệt — tận dụng đúng backend CP5.3/5.4 đã có sẵn nhưng frontend chưa từng nối vào.

---

## 1. HƯỚNG A — BỘ GIÁM SÁT LỆCH MIỀN DỮ LIỆU (DOMAIN-SHIFT DETECTOR)

### 1.1. Ý tưởng

Mọi lỗi domain-mismatch mà dự án từng gặp (xem `plan.md` mục 3.0-3.1) đều có 1 điểm chung: **thống kê của tín hiệu đưa vào model tại thời điểm serving lệch khỏi thống kê của dữ liệu lúc train**, nhưng không có gì tự động phát hiện việc này — phải debug thủ công qua nhiều ngày. Ý tưởng: xây 1 module theo dõi thống kê của từng cửa sổ nhịp tim (beat window) **trước khi** đưa vào model, so sánh với phân phối tham chiếu (đo 1 lần từ tập train), tự động cảnh báo khi lệch đáng kể.

**Đóng góp cho paper**: không chỉ là 1 case-study kể lại chuyện đã xảy ra, mà là 1 công cụ tổng quát + thực nghiệm định lượng chứng minh nó bắt được đúng loại lỗi mà chính dự án đã từng mắc phải và các dự án tương tự có thể mắc lại.

### 1.2. Thiết kế kỹ thuật

**Các thống kê cần theo dõi** (đo trên `beat_window` — 187 điểm, **TRƯỚC** khi qua `normalize_window()` ở [backend/service/inference_service.py:66](backend/service/inference_service.py#L66), vì sau chuẩn hoá min-max mọi tín hiệu đều về [0,1] nên sẽ không còn thấy được lệch biên độ gốc):

| Thống kê | Vì sao chọn | Bắt được loại lỗi nào |
|---|---|---|
| min/max/mean/std biên độ thô | Kaggle train data đã chuẩn hoá sẵn về thang riêng; PhysioNet thô là mV thật (~-3.5 đến 3.65mV cho record 208) | Lỗi quên chuẩn hoá/lọc nhiễu (chính lỗi đã gặp ở CP3.0: 0.2% accuracy) |
| Tỉ lệ zero-pad (`beat_len < window_size` trong `extract_beat_window`, [qrs_detector.py:135](backend/core/qrs_detector.py#L135)) | Train data có đuôi zero-pad theo phân phối nhịp tim thật; nếu tỉ lệ pad lệch nhiều nghĩa là giả định fs/nhịp tim sai | Lỗi sai `fs` khai báo, hoặc lỗi resample sai bước (chính lỗi CP3.1: resample từng nhịp thay vì pad/truncate, Accuracy rớt 92%→27%) |
| Khoảng RR (bpm suy ra) có nằm trong dải sinh lý hợp lý (30-300 bpm) | Sanity check độc lập, rẻ | Lỗi phát hiện sai đỉnh R hàng loạt |
| Năng lượng phổ trong dải QRS (5-15Hz) so với tổng năng lượng | Tín hiệu đã lọc đúng phải tập trung năng lượng đúng dải | Lỗi quên lọc bandpass/notch |

**Phương pháp thống kê**: đơn giản, đủ chặt chẽ để defend trong paper — không cần thứ gì quá phức tạp:
1. Tính **phân phối tham chiếu** 1 lần offline: chạy qua `data/processed/X_train_kaggle.npy` (đã có sẵn), lưu mean/std của từng thống kê trên vào 1 file nhỏ (`saved_models/domain_reference_stats.json`).
2. Runtime: giữ 1 cửa sổ trượt N=50 nhịp gần nhất (đúng quy ước `HRVTracker.max_history` đã dùng ở `backend/core/hrv.py`), tính z-score hoặc khoảng cách Mahalanobis so với tham chiếu.
3. Vượt ngưỡng (vd |z| > 3, tuỳ chỉnh qua thực nghiệm) → ghi cảnh báo + tăng bộ đếm.

**File cần tạo mới**:
- `backend/core/domain_monitor.py` — class `DomainShiftMonitor`, hàm `check(beat_window_raw) -> {is_shifted: bool, z_scores: dict, details: str}`, tương tự cách `HRVTracker` đã được thiết kế (1 instance riêng/kết nối WS).
- `backend/scripts/compute_domain_reference.py` — script offline tính thống kê tham chiếu từ `X_train_kaggle.npy`, ghi ra `saved_models/domain_reference_stats.json`.
- `backend/scripts/evaluate_domain_monitor.py` — script thực nghiệm cho paper (xem mục 1.3).

**Tích hợp vào pipeline hiện có** (thay đổi tối thiểu, không phá vỡ luồng cũ):
- `backend/service/data_streamer.py::ecg_file_reader()`: gọi `monitor.check()` mỗi khi cắt được 1 nhịp mới (đúng chỗ đang gọi `extract_beat_window`).
- `backend/api/ws_routes.py`: thêm field tuỳ chọn vào payload WS, vd `"domain_alert": bool` (mặc định `false`, không phá schema cũ — frontend cũ vẫn chạy được nếu bỏ qua field lạ).
- Có thể thêm 1 bảng nhẹ `domain_alerts` (id, record_id, timestamp_ms, detail JSON) nếu muốn lưu lại lịch sử để phân tích cho paper — dùng chung pattern với `AnomalyEvent`.

### 1.3. Thiết kế thực nghiệm đánh giá (phần quan trọng nhất để thành paper, không chỉ là feature)

**Positive control — tái tạo đúng các lỗi đã biết trong lịch sử dự án** (đây là điểm mạnh nhất: có sẵn ground-truth "lỗi thật đã từng ship"):
1. Bỏ qua bước resample 360→125Hz (đưa thẳng tín hiệu 360Hz-domain vào model).
2. Bỏ qua `bandpass_filter`/`notch_filter`.
3. Dùng `scipy.signal.resample()` per-beat thay vì pad/truncate — **chính xác lỗi đã ship ở CP3.1**.
4. Đưa tín hiệu biên độ mV thô, không qua `normalize_window`.

Với mỗi kịch bản, đo: (a) detector có gắn cờ cảnh báo không, (b) cảnh báo sau bao nhiêu nhịp kể từ lúc lỗi bắt đầu, (c) đối chiếu với accuracy thật đo bằng `validate_classification.py` (đã có sẵn) — chứng minh "cảnh báo sớm" tương quan với "accuracy rớt thật".

**Negative control**: chạy qua toàn bộ 8 bản ghi đã validate (100, 208, 207, 213, 119, 234, 200, 203) ở chế độ đúng (baseline hiện tại), đo tỉ lệ báo động giả (phải gần 0%).

**Bảng kết quả mẫu cho paper**:
| Kịch bản | Accuracy thật (validate_classification.py) | Detector cảnh báo? | Số nhịp tới lúc cảnh báo |
|---|---|---|---|
| Baseline đúng (8 bản ghi) | 94.33% | Không (0% false positive) | — |
| Thiếu resample 125Hz | ~22.9% (số đã đo ở CP3.0) | ? | ? |
| Resample per-beat sai | ~27% (số đã đo ở CP3.1) | ? | ? |
| Thiếu lọc nhiễu hoàn toàn | ~0.2% (số đã đo ở CP3.0) | ? | ? |

(Dấu `?` là số cần đo thật khi build xong — đây chính là kết quả thực nghiệm cốt lõi của paper.)

### 1.4. Sub-checkpoints

- [ ] A1. Viết `compute_domain_reference.py`, chạy ra `domain_reference_stats.json` từ tập train hiện có.
- [ ] A2. Viết `DomainShiftMonitor` (`domain_monitor.py`), unit test với dữ liệu giả lập biết trước là lệch/không lệch.
- [ ] A3. Tích hợp vào `data_streamer.py` + `ws_routes.py` (field `domain_alert` trong payload, không phá schema cũ).
- [ ] A4. Viết `evaluate_domain_monitor.py` — chạy đủ 4 kịch bản positive control + baseline negative control, xuất bảng số liệu.
- [ ] A5. (Tuỳ chọn, nếu muốn trực quan cho demo/paper) thêm badge cảnh báo nhỏ trên Dashboard khi `domain_alert=true`.
- [ ] A6. Viết phần "Method" + "Experiments" của paper dựa trên số liệu A4.

---

## 2. HƯỚNG B — CONFORMAL PREDICTION CHO HÀNG ĐỢI DUYỆT CỦA BÁC SĨ

### 2.1. Ý tưởng

Backend CP5.3/CP5.4 đã có đầy đủ: `GET /api/anomalies` (lịch sử), `POST /api/anomalies/{id}/verify` (bác sĩ duyệt/sửa nhãn), `confidence` (softmax của lớp dự đoán) lưu sẵn trong `AnomalyEvent.confidence`. **Nhưng chưa có UI nào ở frontend gọi tới 2 API này** — đây là gap đã phát hiện lúc review PR #17 gần đây. Ý tưởng: xây UI này VÀ làm nó thông minh hơn bằng conformal prediction — thay vì bác sĩ duyệt theo thứ tự thời gian, ưu tiên duyệt trước những nhịp mô hình **không chắc chắn nhất** (tập dự đoán lớn), theo đúng lý thuyết conformal prediction với đảm bảo coverage toán học — khác với cách làm "ngưỡng confidence" thô hiện tại ở CP4.5.

**Đóng góp cho paper**: có 1 paper 2025 làm đúng ý tưởng này ([Springer, Conformal Prediction for ECG Interpretation](https://link.springer.com/chapter/10.1007/978-3-031-95838-0_14)) nhưng dừng ở nghiên cứu offline trên dataset. Điểm khác biệt của hướng B: gắn vào **1 hệ thống đang chạy thật** (real-time WS + RBAC + audit trail đã có), đo được **tiết kiệm thời gian duyệt thật** — không chỉ coverage lý thuyết.

### 2.2. Thay đổi cần thiết ở backend

- **`backend/service/inference_service.py::predict()`** ([inference_service.py:41](backend/service/inference_service.py#L41)): hiện chỉ trả `confidence` của lớp được chọn (`probs[0, pred_class]`). Cần thêm giá trị trả về thứ 5: toàn bộ vector xác suất 5 lớp (`probs[0].tolist()`) — **đây là thay đổi bắt buộc**, vì conformal prediction cần xác suất của MỌI lớp, không chỉ lớp được chọn, để tính non-conformity score.
- **Script hiệu chỉnh (calibration) mới**: `backend/scripts/calibrate_conformal.py` — dùng lại đúng hạ tầng `evaluate_record()` của `validate_classification.py`, nhưng lấy full probability vector thay vì chỉ argmax. Chia 8 bản ghi đã có thành tập hiệu chỉnh (vd 100, 119, 200) và tập đánh giá (vd 208, 207, 213, 234, 203) — **phải tách rõ, không dùng chung 1 tập để hiệu chỉnh rồi lại đánh giá coverage trên chính nó** (lỗi phương pháp luận kinh điển, đúng thứ mà paper `arXiv 2503.07276` phê bình).
- **`backend/api/anomalies.py`**: `GET /api/anomalies` tính thêm `prediction_set_size` (không cần lưu DB, tính on-the-fly từ `confidence` + ngưỡng hiệu chỉnh — đơn giản hơn migrate schema); thêm tham số sort `?sort_by=uncertainty` bên cạnh mặc định theo thời gian.

### 2.3. Frontend cần xây (hiện chưa tồn tại — đây là phần UI còn thiếu từ trước)

- Trang/tab mới (hoặc mở rộng `XAIPage.jsx`) hiển thị danh sách `GET /api/anomalies`, sắp xếp theo độ bất định, có nút gọi `POST /api/anomalies/{id}/verify` (chỉ hiện với role `doctor`/`admin`, dùng `useAuth()` đã có sẵn từ CP5.5).
- Hiển thị rõ "tập dự đoán" (vd "Model không chắc giữa: NHỊP THẤT (V) / HỢP NHẤT (F)") thay vì chỉ 1 nhãn — đúng tinh thần conformal prediction, giúp bác sĩ hiểu tại sao cần xem kỹ ca này.

### 2.4. Thiết kế đánh giá

1. **Kiểm chứng coverage**: trên tập đánh giá (208, 207, 213, 234, 203), với mức tin cậy chọn trước (vd 90%), đo tỉ lệ thật % nhãn đúng nằm trong tập dự đoán — phải xấp xỉ đúng 90% (nếu lệch nhiều nghĩa là hiệu chỉnh sai hoặc tập hiệu chỉnh không đại diện).
2. **Mô phỏng tiết kiệm thời gian duyệt**: giả sử bác sĩ chỉ đủ thời gian duyệt top-K% ca có độ bất định cao nhất — so sánh tỉ lệ bắt được các ca AI dự đoán SAI thật (so với nhãn bác sĩ .atr) giữa cách sắp theo conformal set size vs sắp theo thời gian (baseline hiện tại) vs sắp theo confidence thô (CP4.5). Đây là số liệu thuyết phục nhất cho paper.

### 2.5. Sub-checkpoints

- [ ] B1. Sửa `predict()` trả thêm full probability vector.
- [ ] B2. Viết `calibrate_conformal.py`, tách calibration/eval set rõ ràng, xuất ngưỡng hiệu chỉnh.
- [ ] B3. Thêm `prediction_set_size`/`sort_by=uncertainty` vào `GET /api/anomalies`.
- [ ] B4. Xây UI hàng đợi duyệt (phần đang thiếu hoàn toàn) + nút verify/correct.
- [ ] B5. Chạy thực nghiệm coverage + mô phỏng tiết kiệm thời gian, ra số liệu cho paper.

---

## 3. TÀI NGUYÊN CẦN CÓ

- Dữ liệu: `data/raw/physionet_mitdb/` (đã có, 48 bản ghi) — đủ cho cả 2 hướng, không cần tải thêm gì mới.
- Không cần train lại model — cả 2 hướng đều dùng `saved_models/resnet1d.pth` hiện có, chỉ thêm tầng phân tích/giám sát bên ngoài.
- Không cần GPU — mọi thực nghiệm đều chạy CPU như hiện tại (đã đo latency 0.13-1.1ms/nhịp).

## 4. RỦI RO & GIỚI HẠN (nói thật, không tô hồng)

- **Hướng A**: ngưỡng z-score/Mahalanobis cần tinh chỉnh thực nghiệm — có thể cần vài vòng thử để cân bằng giữa bắt được lỗi thật (positive control) và không báo động giả (negative control) trên đúng 8 bản ghi hiện có (mẫu số nhỏ, cần nói rõ giới hạn này trong paper thay vì giấu đi).
- **Hướng B**: 8 bản ghi hiện có chia calibration/eval sẽ cho tập rất nhỏ (không phải chuẩn 1 nghìn+ mẫu như paper conformal prediction thường dùng) — coverage đo được có thể dao động nhiều, cần nêu rõ đây là "proof-of-concept trên tập nhỏ", không phải benchmark quy mô lớn. Muốn số liệu vững hơn có thể cần tải thêm bản ghi PhysioNet ngoài 8 bản đã dùng (48 bản ghi có sẵn trong `data/raw/physionet_mitdb/`, chỉ 8/48 đã được dùng để validate).
- Cả 2 hướng đều KHÔNG đụng vào model/pipeline AI đã validate 94.33% — chỉ thêm tầng phân tích bên ngoài, nên rủi ro hồi quy tính năng hiện có gần như bằng 0.

## 5. TÀI LIỆU THAM KHẢO

- [A Systematic Review of ECG Arrhythmia Classification: Adherence to Standards, Fair Evaluation, and Embedded Feasibility](https://arxiv.org/abs/2503.07276) — căn cứ chính cho Hướng A.
- [Conformal Prediction for ECG Interpretation: A Study on Human-AI Collaboration in Clinical Decision Support](https://link.springer.com/chapter/10.1007/978-3-031-95838-0_14) — công trình liên quan gần nhất cho Hướng B, cần trích dẫn + nêu rõ điểm khác biệt (hệ thống thật vs nghiên cứu offline).
- [Reducing False Ventricular Tachycardia Alarms in ICU Settings: A Machine Learning Approach](https://arxiv.org/abs/2503.14621) — tham khảo nếu muốn mở rộng thêm hướng giảm báo động giả trong tương lai.
- Lịch sử domain-mismatch của chính dự án: [plan.md](plan.md) mục 3.0-3.1 (số liệu 0.2%→22.9%→94.33%).
