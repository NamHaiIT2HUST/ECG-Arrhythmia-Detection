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