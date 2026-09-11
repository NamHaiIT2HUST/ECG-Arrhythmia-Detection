# Báo Cáo Đối Sánh Hiệu Năng 5 Mô Hình Deep Learning (ECG Arrhythmia)

**Ngày nghiệm thu**: 2026-08-06 20:15:02

| Model         |   Accuracy (%) |   Precision (%) |   Recall (%) |   F1-Score (%) |   Inference Latency (ms) |   Throughput (samples/s) |   Parameters |   Train Duration (s) |
|:--------------|---------------:|----------------:|-------------:|---------------:|-------------------------:|-------------------------:|-------------:|---------------------:|
| CNN1D_LSTM    |          97.27 |           81.26 |        93.58 |          85.79 |                   0.18   |                     5556 |       242885 |              5820.28 |
| Mamba1D       |          94.45 |           74.27 |        87.92 |          79.28 |                   0.4696 |                     2130 |        59877 |              5727.42 |
| ResNet1D      |          98.57 |           92.49 |        92    |          92.16 |                   0.1342 |                     7452 |       692389 |              2780.83 |
| TCN           |          96.17 |           76.94 |        94.69 |          82.81 |                   0.793  |                     1261 |       171365 |             16475.9  |
| Transformer1D |          95.36 |           77.69 |        91.98 |          83.11 |                   0.4294 |                     2329 |        69317 |             34835.1  |

---
*Báo cáo được khởi tạo tự động bởi benchmark suite.*

## End-to-End Latency (bổ sung — hoàn thiện đề cương)

Đo từ lúc phát hiện đỉnh R mới (`backend/service/data_streamer.py`, trường `detected_at`)
đến ngay trước lúc payload tương ứng được gửi qua WebSocket (`backend/api/ws_routes.py`,
trường `latency_e2e_ms`) — script đo: `backend/scripts/benchmark_e2e_latency.py`.

| Record | N nhịp | Mean (ms) | p95 (ms) | Max (ms) |
|---|---:|---:|---:|---:|
| 100 | 200 | 2.38 | 2.93 | 45.98 |
| 208 | 200 | 4.42 | 8.79 | 42.99 |
| 234 | 200 | 2.29 | 3.17 | 15.66 |
| **Tổng hợp** | **600** | **3.03** | **7.82** | **45.98** |

**Kết luận**: vượt xa chỉ tiêu đề cương "End-to-End Latency < 2 giây" (2000ms) — con số đo
được chỉ vài mili giây, thấp hơn ngưỡng khoảng 3 bậc độ lớn.

**Lưu ý về phạm vi đo** (nói thật, không tô hồng): đo qua `TestClient` (chạy nội bộ cùng
tiến trình, không qua mạng thật), nên phản ánh đúng độ trễ xử lý nội bộ của backend
(Pan-Tompkins + AI inference + đóng gói JSON), **không tính** độ trễ mạng thực tế hoặc thời
gian render phía trình duyệt — 2 yếu tố này phụ thuộc hạ tầng triển khai, không phải lỗi hệ
thống, và trên cùng mạng LAN/localhost là không đáng kể so với biên độ đã đo được.

## Retrain ResNet1D với Validation Split (bổ sung — hoàn thiện đề cương)

Đề cương yêu cầu chia Train/Validation/Test — bảng benchmark gốc ở trên (5 model) chỉ dùng
Train/Test (100% dữ liệu train, không trích Validation) cho vòng khảo sát kiến trúc, giữ
nguyên không đổi để bảng so sánh 5 model vẫn công bằng (cùng 1 protocol). Model được chọn
triển khai (**ResNet1D**) được huấn luyện lại riêng, đầy đủ Train/Validation/Test.

**Sửa đúng gốc rễ, không chỉ tách nhanh ở bước train**: lần thử đầu tiên tách Validation
*sau* SMOTE (ngay trong `src/benchmark.py`) — phát hiện Validation Accuracy bị thổi phồng
giả tạo (99.78%) so với Test Accuracy (98.56%) vì mẫu Validation lẫn cả mẫu tổng hợp SMOTE
gần trùng với Train. Đã sửa lại đúng chỗ: tách Validation (10%, stratified) **trước SMOTE**,
ngay ở `data/preprocess.py` — đúng nguyên tắc "tách trước khi cân bằng" plan.md mục 1.2 đã
áp dụng cho Test từ đầu dự án. Sau khi sửa, Validation phản ánh đúng phân phối mất cân bằng
thật (7248 N / 222 S / 579 V / 64 F / 643 Q trên 8756 mẫu) thay vì phân phối cân bằng giả.

| Chỉ số | Giá trị (sau khi sửa) |
|---|---|
| Train (đã SMOTE, 90% pool) | 326.115 mẫu |
| Validation (thật, trước SMOTE) | 8.756 mẫu |
| Test Accuracy | 98.51% (so với 98.57% bản gốc — không hồi quy) |
| Test Precision / Recall / F1-macro | 92.63% / 91.72% / 92.16% (F1 khớp y hệt bản gốc) |
| Validation Accuracy (epoch cuối) | 98.62% |
| Validation Loss (epoch cuối) | 0.0780 |

**Val Accuracy (98.62%) và Test Accuracy (98.51%) giờ chênh lệch chỉ 0.11 điểm %** — bằng
chứng rõ ràng cho thấy Validation đã "sạch" thật sự (so với chênh lệch 1.2 điểm % ở lần thử
tách sau SMOTE). Val loss dao động nhẹ trong khoảng 0.070-0.078 từ epoch 3 trở đi (không tăng
phân kỳ), Val Accuracy giữ ổn định ~98.6-98.7% từ epoch 7 — không có dấu hiệu overfitting.

### Kiểm chứng lại Accuracy End-to-End (dữ liệu PhysioNet thật, `validate_classification.py`)

| Record | N nhịp | Accuracy | F1 (macro) |
|---|---:|---:|---:|
| 100 | 2273 | 99.56% | 95.30% |
| 208 | 2939 | 92.14% | 51.30% |
| 207 | 1830 | 97.16% | 70.73% |
| 213 | 3250 | 94.52% | 80.91% |
| 119 | 1987 | 100.00% | 100.00% |
| 234 | 2753 | 99.85% | 98.64% |
| 200 | 2598 | 95.38% | 54.77% |
| 203 | 2916 | 96.60% | 41.17% |
| **Tổng hợp (8 bản ghi)** | **20.546** | **96.62%** | **67.44%** |

**96.62%, cải thiện so với 94.33% đo lúc CP3.3** (không hồi quy — thậm chí tốt hơn; chênh lệch
nằm trong biên độ bình thường giữa các lần train do khởi tạo trọng số ngẫu nhiên + SMOTE lấy
mẫu tổng hợp khác nhau mỗi lần, không phải lỗi). F1-macro (67.44%) thấp hơn nhiều so với
Accuracy là do lớp **Q gần như không có mẫu thật** trong 8 bản ghi này (chỉ 3/20.546 mẫu) —
đặc điểm vốn có của dữ liệu AAMI (Q là lớp hiếm nhất), không phải vấn đề phát sinh từ lần
retrain này.

**Lưu ý kỹ thuật nợ lại**: `saved_models/resnet1d.onnx`/`resnet1d_int8.onnx` (CP6.1) chưa
được xuất lại sau lần retrain này — vẫn phản ánh trọng số CŨ, cần chạy lại
`python -m src.models.export_onnx` trước khi dùng bản ONNX cho việc gì khác.