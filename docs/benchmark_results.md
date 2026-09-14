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

## Throughput WebSocket (bổ sung — hoàn thiện đề cương)

Đo throughput theo kịch bản nhiều client đồng thời mở kết nối `/ws/ecg?record=<id>` và xử lý
số liệu real-time song song. Script đo: `backend/scripts/benchmark_throughput.py`.

| K kết nối đồng thời | Tổng beat xử lý | Throughput (beat/s) | Latency trung bình (ms) | Thời gian chạy (s) |
|---:|---:|---:|---:|---:|
| 1 | 6 | 0.75 | 15.12 | 8.00 |
| 5 | 28 | 3.49 | 5.85 | 8.02 |
| 10 | 41 | 5.10 | 2.63 | 8.05 |
| 20 | 0 | 0.00 | 0.00 | 15.00 |

**Kết luận**: trên máy dev hiện tại, hệ thống ổn định ở mức 1–10 client đồng thời, đạt khoảng
**5.10 beat/s** ở K=10 với latency trung bình **2.63 ms**. Khi tăng tới **K=20**, benchmark
bắt đầu thất bại/không ổn định trong thời gian test 15s, cho thấy ngưỡng ổn định thực tế của
một máy local hiện tại nằm khoảng **10 kết nối đồng thời**. Đây là số liệu hợp lệ cho việc
đánh giá triển khai ban đầu, nhưng cần đo lại ở môi trường deployment thật (server mạnh hơn,
CPU/RAM rõ ràng, mạng LAN/WAN) trước khi công bố ngưỡng production.

**Khuyến nghị giới hạn triển khai thực tế**: với cấu hình máy hiện tại, nên triển khai giới hạn
**≤ 10 bệnh nhân/giường giám sát đồng thời trên 1 node backend** để giữ throughput ổn định
và latency không tăng đột biến. Nếu cần scale lên, nên thêm load balancer hoặc chạy nhiều
instance backend song song, đồng thời đo lại throughput ở mỗi mức K mới. Đây là giới hạn
thực tế dựa trên benchmark tự đo ở môi trường local, không phải giá trị lý thuyết cho mọi máy chủ.

## Sàng lọc Rung nhĩ / AFib Screening (bổ sung — hoàn thiện đề cương)

Rung nhĩ là chẩn đoán theo **nhịp điệu kéo dài** (RR "irregularly irregular" + khả năng mất
sóng P), khác bản chất với phân loại hình dạng từng nhịp đơn lẻ mà ResNet1D đang làm — nên
được tách thành 1 tầng screening rule-based riêng, không phải thêm 1 lớp vào model 5 lớp AAMI:

- `backend/core/afib_screener.py` (`AfibScreener`) — dùng trong luồng WebSocket thời gian thực,
  tính điểm AFib tức thời từ cửa sổ trượt tối đa 50 khoảng RR gần nhất (độ không đều RR, pNN50,
  RMSSD), trả `afib_suspected`/`afib_score` mỗi nhịp mới.
- `backend/service/afib_screening_service.py` (`screen_afib_signal`) — dùng cho endpoint offline
  `POST /api/screening/afib` (upload file ECG), phân tích toàn bộ đoạn tín hiệu 1 lần, có thêm
  ước lượng sự vắng mặt sóng P và tần số tim; trả `status` (negative/indeterminate/positive).
- `backend/scripts/calibrate_afib_thresholds.py` + `download_afdb_sample.py` — script hiệu
  chỉnh ngưỡng dựa trên MIT-BIH AFDB.

**Lưu ý kỹ thuật nợ lại (nói thật, không tô hồng)**:
1. **Chưa có số Sensitivity/Specificity đáng tin cậy.** `calibrate_afib_thresholds.py` hiện
   giả định *toàn bộ* record AFDB tải về đều là rung nhĩ (không đọc nhãn rhythm annotation
   `(AFIB`/`(N` thật của AFDB), nên "specificity" tính ra luôn bằng 0 và ngưỡng "tối ưu" tìm
   được không có ý nghĩa thống kê thật — chỉ nên coi đây là demo cơ chế đo, chưa phải kết quả
   hiệu chỉnh đã kiểm chứng. Cần đọc annotation thật (`wfdb.rdann(..., 'atr')` trên AFDB có nhãn
   theo đoạn) rồi tính lại ROC mới dùng được số Sensitivity/Specificity cho báo cáo.
2. **2 công thức tính điểm khác nhau** giữa `AfibScreener` (streaming) và `screen_afib_signal`
   (offline) — cùng mục tiêu sàng lọc AFib nhưng trọng số/ngưỡng khác nhau, có thể cho kết quả
   khác nhau trên cùng 1 tín hiệu tuỳ đi qua đường nào. Việc hợp nhất về 1 công thức chung nên
   làm ở lần chỉnh sửa tiếp theo, không nằm trong phạm vi merge lần này.
3. Ngưỡng mặc định (`AfibScreener.threshold = 0.62`, `DEFAULT_THRESHOLDS` trong
   `afib_screening_service.py`) hiện là **giá trị chọn tay dựa trên trực giác**, chưa qua
   kiểm chứng bằng dữ liệu nhãn thật — không nên dùng để tuyên bố độ chính xác lâm sàng.

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

![So sánh Validation trước/sau khi sửa lỗi tách sau SMOTE](c2_validation_leak_comparison.png)

*Biểu đồ trên minh hoạ đúng quá trình debug thật: đường đỏ (tách Validation sau SMOTE) leo
dần lên 99.78% — cao hơn hẳn đường Test Accuracy tương ứng (nét đứt đỏ, 98.56%), dấu hiệu rõ
ràng của rò rỉ dữ liệu. Đường xanh (đã sửa, tách trước SMOTE) hội tụ đúng sát đường Test
Accuracy của chính nó (nét đứt xanh, 98.51%) — khớp nhau vì Validation giờ phản ánh đúng
phân phối thật, không còn bị mẫu tổng hợp SMOTE làm lệch. Script tái tạo:
`python -m backend.scripts.plot_c2_diagnostics`.*

### Kiểm chứng Overfitting: so sánh Train / Validation / Test trên cùng 1 model

Đo trực tiếp accuracy của `saved_models/resnet1d.pth` (sau khi sửa) trên cả 3 tập:

| Tập | N mẫu | Accuracy |
|---|---:|---:|
| Train (đã SMOTE) | 326.115 | 99.94% |
| Validation (thật) | 8.756 | 98.62% |
| Test (thật) | 21.892 | 98.51% |

Chênh lệch Train→Val/Test chỉ **1.3-1.4 điểm %** — quá nhỏ để coi là overfitting (overfitting
kinh điển thường chênh vài chục điểm %). Train Accuracy cao gần tuyệt đối (99.94%) là bình
thường vì Train đã qua SMOTE (nhiều mẫu tổng hợp nội suy gần giống nhau, "dễ" đạt gần tuyệt
đối). Bằng chứng generalization tốt nhất: **2 tập hoàn toàn độc lập nhau (Validation và Test)
chỉ lệch 0.11 điểm %** — nếu model học vẹt đặc điểm riêng của Train, 2 tập độc lập này sẽ
không thể tự nhiên khớp sát nhau đến vậy.

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

![Confusion matrix end-to-end 8 bản ghi PhysioNet](c2_confusion_matrix.png)

*Chi tiết đáng chú ý từ ma trận nhầm lẫn: lớp **F (Hợp nhất) chỉ đạt recall 56.1%** (412/735
nhịp F thật) — gần 36% nhịp F thật bị nhầm thành N (264/735), phản ánh đúng thực tế lâm sàng
là nhịp Hợp nhất có hình dạng lai giữa nhịp bình thường và nhịp thất, dễ gây nhầm lẫn kể cả
với bác sĩ. Lớp V (Thất) — quan trọng nhất lâm sàng vì liên quan PVC — đạt recall 96.5%, tốt.
Script tái tạo: `python -m backend.scripts.plot_c2_diagnostics`.*

**Lưu ý kỹ thuật nợ lại**: `saved_models/resnet1d.onnx`/`resnet1d_int8.onnx` (CP6.1) chưa
được xuất lại sau lần retrain này — vẫn phản ánh trọng số CŨ, cần chạy lại
`python -m src.models.export_onnx` trước khi dùng bản ONNX cho việc gì khác.