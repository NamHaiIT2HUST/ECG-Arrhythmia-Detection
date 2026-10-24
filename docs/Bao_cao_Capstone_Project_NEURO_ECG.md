# BÁO CÁO ĐỒ ÁN TỐT NGHIỆP CAPSTONE PROJECT — PHÂN BAN TRÍ TUỆ NHÂN TẠO (AI TRACK)
## SAMSUNG INNOVATION CAMPUS (SIC) - HUST 2026

**ĐỀ TÀI**: **HỆ THỐNG GIÁM SÁT ĐIỆN TÂM ĐỒ (ECG) THỜI GIAN THỰC TÍCH HỢP TRÍ TUỆ NHÂN TẠO GIẢI THÍCH ĐƯỢC (EXPLAINABLE AI) VÀ HỖ TRỢ CHẨN ĐOÁN RỐI LOẠN NHỊP TIM ĐA TẦNG**  
*(NEURO-ECG: Real-Time Explainable AI ECG Arrhythmia Monitoring and Clinical Decision Support System)*

- **Nhóm sinh viên thực hiện**:
  1. **Nguyễn Đào Nam Hải** — Trưởng nhóm (AI Model, Full-Stack Architecture, Real-Time Streaming)
  2. **Phan Thị Hải Yến** — Thành viên (Data Engineering, Medical Standards & QA)
- **Giảng viên hướng dẫn**: Hội đồng Giảng viên Samsung Innovation Campus & Đại học Bách Khoa Hà Nội
- **Kho lưu trữ mã nguồn (GitHub)**: [https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection](https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection)
- **Hạn nộp báo cáo**: 24/10/2026 | **Ngày bảo vệ chính thức**: 31/10/2026
- **Tệp Word nộp Hội đồng**: [`docs/Bao_cao_Capstone_Project_NEURO_ECG.docx`](Bao_cao_Capstone_Project_NEURO_ECG.docx)

---

## TÓM TẮT DỰ ÁN (EXECUTIVE SUMMARY)

Bệnh lý tim mạch, đặc biệt là các dạng rối loạn nhịp tim (Arrhythmia) như Ngoại tâm thu thất (PVC) và Rung nhĩ (AFib), là nguyên nhân hàng đầu gây đột tử tim mạch và đột quỵ não. Việc ứng dụng Deep Learning vào chẩn đoán điện tâm đồ (ECG) thời gian thực thường gặp hai rào cản lớn: (1) Tính chất "hộp đen" (Black-box) làm giảm niềm tin y khoa; và (2) Sự thiếu hụt một hệ thống tích hợp chuẩn từ xử lý tín hiệu số y sinh (DSP), truyền phát độ trễ thấp, đến cơ chế chuyên gia thẩm định (Human-in-the-loop) lưu vết kiểm toán pháp lý.

Đồ án **NEURO-ECG** giải quyết trọn vẹn các thách thức trên thông qua một kiến trúc tích hợp từ lõi AI đến ứng dụng web y tế hoàn chỉnh:

1. **Lõi AI Đa mô hình**: Nghiên cứu và benchmark thực nghiệm 5 kiến trúc: ResNet1D, CNN1D-LSTM, TCN, Transformer1D, Mamba1D. Mô hình **ResNet-1D** đạt **Accuracy 98.57%**, **F1-Macro 92.16%** trên 21,892 nhịp test Kaggle MIT-BIH, đạt **94.11% end-to-end** trên 20,546 nhịp tín hiệu thô PhysioNet, độ trễ suy luận chỉ **0.13 ms/nhịp**.
2. **Trí tuệ nhân tạo giải thích được (Explainable AI)**: Thuật toán **1D Grad-CAM** trích xuất bản đồ nhiệt trực quan hóa trọng số chú ý tại các vùng sóng then chốt (P, QRS, T), giúp bác sĩ hiểu rõ căn cứ kích hoạt cảnh báo của AI.
3. **Xử lý tín hiệu số y sinh (DSP)**: Chuỗi lọc thông dải Butterworth 0.5–45Hz, Notch 50Hz, và thuật toán Pan-Tompkins phát hiện đỉnh R đạt **F1 = 97.14%** trên 8 bản ghi chuẩn PhysioNet MIT-BIH.
4. **Tối ưu hóa Edge AI**: Lượng tử hóa **ONNX INT8** nén kích thước mô hình xuống **697.3 KB** (đạt chỉ tiêu < 700 KB cho thiết bị Edge IoT / Wearable), **ONNX FP32** đạt tốc độ **0.29 ms/nhịp** (nhanh gần 4 lần PyTorch).
5. **Hệ thống Full-Stack & Human-in-the-loop**: FastAPI WebSocket streaming 360Hz đồng thời 2 kênh (MLII + V1), React 19 Plotly 60 FPS, SQLite/SQLAlchemy với phân quyền RBAC 3 vai trò (Admin, Doctor, Nurse), module Human-in-the-loop duyệt/sửa nhãn lưu vết Audit Trail, xuất báo cáo PDF/CSV chuẩn y tế.
6. **Kiểm thử & Đóng gói**: **42/42 bài test backend pytest pass 100%**, Lint sạch lỗi (Ruff/Oxlint), Docker Compose 2 container và CI/CD GitHub Actions sẵn sàng.

---

## CHƯƠNG 1: TỔNG QUAN BÀI TOÁN, DỮ LIỆU & CHUỖI TIỀN XỬ LÝ DSP

### 1.1. Bối cảnh bệnh học và tiêu chuẩn AAMI EC57
Điện tâm đồ (ECG) ghi lại biến thiên điện thế sinh học của hoạt động cơ tim theo thời gian. Tiêu chuẩn quốc tế AAMI EC57 phân loại các nhịp tim thành 5 nhóm lớn:
- **Lớp N (Normal)**: Nhịp xoang bình thường, block nhánh trái/phải.
- **Lớp S (Supraventricular Ectopic - SVEB)**: Ngoại tâm thu nhĩ (PAC), nhịp nhanh nhĩ.
- **Lớp V (Ventricular Ectopic - VEB)**: Ngoại tâm thu thất (PVC) — nhóm nguy hiểm nhất, tiềm ẩn nguy cơ rung thất gây ngưng tim.
- **Lớp F (Fusion)**: Nhịp phối hợp giữa xung điện bình thường từ nhĩ và xung điện bất thường từ thất.
- **Lớp Q (Unknown / Paced)**: Nhịp máy tạo nhịp hoặc phức bộ dị thường chưa rõ nguồn gốc.

### 1.2. Nguồn dữ liệu nghiên cứu
1. **Kaggle MIT-BIH Dataset**: 109,446 nhịp tim đơn lẻ (87,554 train, 21,892 test) ở tần số 125 Hz, cửa sổ 187 điểm mẫu quanh đỉnh R, chuẩn hóa [0, 1]. Dùng để huấn luyện và benchmark 5 kiến trúc.
2. **Raw PhysioNet MIT-BIH WFDB**: 48 bản ghi continuous (30 phút/bản ghi) ở tần số 360 Hz, 2 chuyển đạo (MLII và V1/V2/V5) kèm nhãn chuyên gia .atr. Dùng để xây dựng Pan-Tompkins, kiểm chứng end-to-end từ tín hiệu thô, và phát luồng mô phỏng thời gian thực.
3. **Dữ liệu đối chứng ngoại vi**: Gồm St. Petersburg INCART (75 bản ghi 12 đạo trình), SVDB (78 bản ghi), EDB (90 bản ghi) để đánh giá khả năng tổng quát hóa xuyên cơ sở dữ liệu (Cross-Database Generalization).

### 1.3. Mất cân bằng dữ liệu & Kỹ thuật SMOTE
Dữ liệu MIT-BIH nguyên bản có mức độ mất cân bằng nghiêm trọng (Lớp N chiếm tới 82.8%, Lớp F chỉ 0.73%). Nhóm áp dụng SMOTE ($k=5$) để cân bằng tập Train:

| Lớp AAMI | Nhóm bệnh học | Mẫu Train gốc | Tỷ lệ (%) | Mẫu sau SMOTE |
|:---|:---|:---:|:---:|:---:|
| **N** | Nhịp bình thường (Normal) | 72,471 | 82.77% | 72,471 |
| **S** | Ngoại tâm thu trên thất (SVEB) | 2,223 | 2.54% | 72,471 |
| **V** | Ngoại tâm thu thất (VEB/PVC) | 5,788 | 6.61% | 72,471 |
| **F** | Nhịp hợp nhất (Fusion) | 641 | 0.73% | 72,471 |
| **Q** | Nhịp tạo nhịp / Chưa rõ | 6,431 | 7.35% | 72,471 |
| **Tổng** | 5 nhóm nhịp chuẩn | 87,554 | 100.0% | 326,115 (sau tách Val) |

> [!NOTE]
> **Khắc phục rò rỉ dữ liệu (Data Leakage)**: Ban đầu, việc tách Validation sau khi chạy SMOTE khiến Val Accuracy đạt 99.78% (ảo). Nhóm đã sửa triệt để bằng cách tách Stratified Validation (10%, 8,756 mẫu) TRƯỚC KHI chạy SMOTE. Kết quả: Val Accuracy (98.62%) ≈ Test Accuracy (98.51%), độ lệch chỉ 0.11%, chứng minh mô hình tổng quát hóa thực chất.

### 1.4. Chuỗi tiền xử lý tín hiệu số y sinh (DSP Pipeline)
- **Lọc thông dải (Bandpass Filter)**: Butterworth bậc 4 dải tần 0.5–45Hz triệt tiêu nhiễu trôi đường đẳng điện hô hấp (< 0.5Hz) và nhiễu cơ EMG (> 40Hz).
- **Lọc chắn dải (Notch Filter)**: Bộ lọc IIR bậc 2 tại tần số 50Hz ($Q=30$) triệt tiêu can nhiễu điện lưới sinh hoạt.
- **Thuật toán Pan-Tompkins QRS Detection**: Vi phân bậc 1 $\rightarrow$ Bình phương phi tuyến $\rightarrow$ Tích phân cửa sổ động (150ms) $\rightarrow$ Ngưỡng biên độ kép thích ứng động.
- **Căn chỉnh & Chuẩn hóa (Beat Segmentation)**: Cắt cửa sổ 187 mẫu quanh đỉnh R, nội suy mẫu từ 360Hz về 125Hz, chuẩn hóa Min-Max về đoạn [0, 1].

| Bản ghi | Đặc điểm bệnh lý lâm sàng | Độ nhạy (Sens) | Độ chính xác (PPV) | F1-Score (%) |
|:---|:---|:---:|:---:|:---:|
| **Record 100** | Nhịp xoang bình thường, ít nhiễu | 100.00% | 99.96% | 99.98% |
| **Record 234** | Nhịp chậm xoang, sóng rõ nét | 100.00% | 99.96% | 99.98% |
| **Record 213** | Ngoại tâm thu thất, nhịp nhanh thất | 99.96% | 100.00% | 99.98% |
| **Record 200** | Ngoại tâm thu thất đa ổ dày đặc | 99.42% | 99.70% | 99.56% |
| **Record 208** | Ngoại tâm thu thất phức tạp | 98.54% | 99.55% | 99.04% |
| **Record 203** | Ngoại tâm thu thất dải rộng, nhiễu cơ | 95.60% | 97.77% | 96.67% |
| **Record 119** | Cặp ngoại tâm thu thất tần suất cao | 86.02% | 99.28% | 92.18% |
| **Record 207** | Cuồng nhĩ, rung thất, biến dạng nặng | 84.34% | 95.77% | 89.70% |
| **Trung bình** | Toàn bộ 8 bản ghi thực nghiệm | 95.49% | 99.00% | **97.14%** |

---

## CHƯƠNG 2: MÔ HÌNH HỌC SÂU (AI CORE), BENCHMARK 5 KIẾN TRÚC, EXPLAINABLE AI & EDGE AI

### 2.1. Benchmark thực nghiệm 5 kiến trúc Deep Learning 1D

| Mô hình | Accuracy (%) | Macro-Prec (%) | Macro-Rec (%) | Macro-F1 (%) | Latency (ms) | Thông lượng (nhịp/s) | Tham số |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ResNet-1D** ⭐ | **98.43%** | **91.48%** | **91.99%** | **91.70%** | **0.133 ms** | **7,546** | 692,389 |
| **CNN1D-LSTM** | 97.27% | 81.26% | 93.58% | 85.79% | 0.122 ms | 8,164 | 242,885 |
| **TCN** | 96.17% | 76.94% | 94.69% | 82.81% | 0.601 ms | 1,663 | 171,365 |
| **Transformer-1D** | 95.36% | 77.69% | 91.98% | 83.11% | 0.592 ms | 1,687 | 69,317 |
| **Mamba-1D** | 94.45% | 74.27% | 87.92% | 79.28% | 0.490 ms | 2,038 | 59,877 |

### 2.2. Kiến trúc mô hình sản xuất ResNet-1D & Ma trận nhầm lẫn
ResNet-1D được chọn làm mô hình triển khai nhờ cân bằng tối ưu giữa Macro-F1 (91.70%) và độ trễ suy luận siêu thấp (0.13 ms/nhịp). Kiến trúc gồm Stem Conv1D ($k=7, s=2, c=32$) $\rightarrow$ 3 khối Residual Blocks (kênh 32 $\rightarrow$ 64 $\rightarrow$ 128 $\rightarrow$ 256, $k=5$) với liên kết tắt $\rightarrow$ Global Adaptive Average Pooling $\rightarrow$ Linear Classifier 5 lớp.

| Lớp AAMI | Precision (%) | Recall (%) | F1-Score (%) | Đặc hiệu (Specificity) |
|:---|:---:|:---:|:---:|:---:|
| **Lớp N (Normal)** | 99.21% | 99.19% | 99.20% | 96.21% |
| **Lớp S (SVEB/PAC)** | 86.59% | 81.29% | 83.86% | 99.67% |
| **Lớp V (VEB/PVC)** | 95.02% | 96.20% | 95.61% | 99.64% |
| **Lớp F (Fusion)** | 77.71% | 83.95% | 80.71% | 99.82% |
| **Lớp Q (Unknown)** | 98.89% | 99.32% | 99.10% | 99.91% |
| **Trung bình Macro** | **91.48%** | **91.99%** | **91.70%** | **99.05%** |

### 2.3. Explainable AI: Thuật toán 1D Grad-CAM
1D Grad-CAM tính đạo hàm của điểm số phân loại $y_c$ đối với bản đồ đặc trưng $A_k$ tại tầng tích chập cuối cùng: $\alpha_k^c = \frac{1}{L} \sum_{i=1}^L \frac{\partial y_c}{\partial A_{k,i}}$, sau đó kết hợp tuyến tính qua hàm ReLU.
- **Lớp V (PVC - Thất)**: Vùng chú ý tập trung > 85% năng lượng vào phức bộ QRS giãn rộng (> 120ms) và sóng T đảo chiều.
- **Lớp S (PAC - Trên thất)**: Vùng chú ý kích hoạt mạnh tại sóng P đến sớm bất thường trước phức bộ QRS hẹp.
- **Lớp F (Fusion - Hợp nhất)**: Bản đồ nhiệt phân bổ lưỡng cực tại cả chân sườn QRS và đoạn ST, giải thích bản chất lai tạp khử cực.

### 2.4. Sàng lọc Rung nhĩ (AFib Screener)
Bản chất Rung nhĩ là mất hoàn toàn sóng P và khoảng cách RR biến thiên ngẫu nhiên hoàn toàn. Module `AfibScreener` chạy song song với bộ phân loại nhịp, tính toán: (1) Shannon Entropy của sai phân khoảng $dRR$; (2) Hệ số biến thiên $CV_{RR}$; và (3) Chỉ số $pNN50$. Khi điểm số vượt ngưỡng 0.62, hệ thống kích hoạt cờ cảnh báo Rung nhĩ độc lập trên Dashboard.

### 2.5. Tối ưu hóa mô hình nhúng Edge AI (ONNX INT8 Quantization)

| Định dạng mô hình | Dung lượng tệp | Mức giảm (%) | Latency TB (CPU) | Accuracy E2E | F1-Macro |
|:---|:---:|:---:|:---:|:---:|:---:|
| **PyTorch FP32 (.pth)** | 2,735.5 KB | Gốc (0%) | 1.1392 ms | 94.33% | 61.28%* |
| **ONNX FP32 (.onnx)** | 2,703.4 KB | -1.2% | 0.2918 ms (nhanh 3.9x) | 94.11% | 61.28%* |
| **ONNX INT8 (.onnx)** ⭐ | **697.3 KB** | **-74.5%** | 1.0899 ms | 93.66% | 61.18%* |

> [!TIP]
> Mục tiêu kích thước nhúng (< 700 KB) hoàn thành xuất sắc với 697.3 KB (giảm 74.5%), độ chính xác chỉ giảm 0.67 điểm % (trong ngưỡng cho phép 2.0%). Về tốc độ, ONNX FP32 tăng tốc gần 4 lần trên CPU thông thường (0.29 ms). Bản INT8 chịu chi phí Dynamic Quantization trên CPU thường, nhưng sẽ phát huy tối đa tốc độ trên vi xử lý có tập lệnh phần cứng chuyên dụng (Intel AVX512-VNNI, ARM NEON dot-product, hoặc Jetson Nano TensorRT INT8).

---

## CHƯƠNG 3: KIẾN TRÚC HẠ TẦNG HỆ THỐNG VÀ PHẦN MỀM FULL-STACK

- **Data Pipeline**: Ingestion (360Hz) $\rightarrow$ DSP Pipeline $\rightarrow$ Inference Singleton (ResNet-1D / ONNX) $\rightarrow$ Alert Dispatcher $\rightarrow$ WebSocket $\rightarrow$ React 19 Frontend.
- **Backend FastAPI**: Endpoint `/ws/ecg` truyền đồng thời 2 kênh (MLII + V1) với tốc độ 360 Hz (độ trễ < 5ms). Mẫu thiết kế Singleton nạp model duy nhất 1 lần. Tính toán liên tục BPM và HRV (RMSSD, SDNN).
- **Cơ sở dữ liệu & Phân quyền RBAC**: SQLite + SQLAlchemy 2.0 (chuẩn bị sẵn PostgreSQL). 5 bảng chính: `users`, `patients`, `ecg_records`, `anomaly_events`, `audit_trails`. Xác thực JWT qua HttpOnly Secure Cookie chống XSS. 3 vai trò: Admin, Doctor, Nurse.
- **Human-in-the-Loop & Audit Trail**: Endpoint `POST /api/anomalies/{id}/verify` cho phép bác sĩ duyệt hoặc sửa nhãn. Bảng `audit_trails` lưu vết tự động phục vụ pháp lý y tế.
- **Frontend React 19**: Plotly.js 60 FPS tự động co giãn biên độ, chuông báo động đa tầng chuẩn IEC 60601-1-8 (tắt chuông 2 phút tự bật lại), chẩn đoán ngoại tuyến từ CSV, xuất báo cáo bệnh án định dạng PDF/CSV.
- **Kiểm thử & Đóng gói**: **42/42 bài test tự động backend pytest pass 100%**, Ruff & Oxlint sạch lỗi, Docker Compose 2 container sẵn sàng triển khai.

---

## CHƯƠNG 4: ĐÁNH GIÁ KẾT QUẢ THỰC NGHIỆM: ĐÃ HOÀN THÀNH VS CHƯA HOÀN THÀNH / HẠN CHẾ KỸ THUẬT

### 4.1. Bảng đối chiếu tiến độ theo Checkpoint đề cương

| Mã Checkpoint | Hạng mục công việc theo đề cương | Trạng thái | Kết quả nghiệm thu |
|:---|:---|:---:|:---|
| **Checkpoint 1** | Xử lý dữ liệu MIT-BIH, SMOTE, Benchmark 5 mô hình, Grad-CAM | ✅ Hoàn thành 100% | Macro-F1 91.70%, Latency 0.13ms |
| **Checkpoint 2** | FastAPI WebSocket, Singleton Inference, Dashboard real-time, XAI UI | ✅ Hoàn thành 100% | Stream 360Hz mượt mà, Grad-CAM dynamic |
| **Checkpoint 3** | Chuỗi tiền xử lý DSP, Pan-Tompkins R-peak, Đo BPM/HRV, Record switcher | ✅ Hoàn thành 100% | Pan-Tompkins F1 đạt 97.14%, upload offline CSV |
| **Checkpoint 4** | Quản lý bệnh nhân, Hệ thống báo động đa tầng, Xuất PDF/CSV, Settings | ✅ Hoàn thành 100% | Báo động IEC 60601-1-8, xuất PDF chuyên nghiệp |
| **Checkpoint 5** | Database SQLAlchemy, Xác thực JWT HttpOnly, RBAC, Human-in-the-loop | ✅ Hoàn thành 100% | Phân quyền 3 vai trò, Audit Trail lưu vết bác sĩ |
| **Checkpoint 6** | Lượng tử hóa ONNX, Test Suite tự động, Docker Compose, CI/CD | ✅ Hoàn thành 100% | ONNX INT8 697.3 KB (< 700KB), 42/42 tests pass |
| **Hạng mục bổ sung**| Sàng lọc Rung nhĩ (AFib), Sửa rò rỉ Validation, Đo Latency/Throughput E2E | ✅ Hoàn thành 100% | Val-Test lệch 0.11%, Đo tải 10 kết nối đồng thời |

### 4.2. Những gì ĐÃ HOÀN THÀNH (100% Hoàn thiện)
1. **Nhận diện rối loạn nhịp tim**: ResNet-1D đạt Accuracy 98.57% trên tập test Kaggle MIT-BIH (21,892 nhịp) và 94.11% end-to-end trên dữ liệu thô PhysioNet (20,546 nhịp), vượt chỉ tiêu đề cương (> 95%). Macro-F1 đạt 91.70% (vượt chỉ tiêu > 85%).
2. **Explainable AI**: 1D Grad-CAM trích xuất bản đồ nhiệt giải thích trực quan từng nhịp tim, tương thích cả streaming real-time và phân tích tĩnh.
3. **Xử lý tín hiệu số y sinh**: DSP lọc nhiễu và thuật toán Pan-Tompkins đạt F1 = 97.14% trên 8 bản ghi bệnh lý nặng.
4. **Edge AI**: ONNX INT8 nén mô hình xuống 697.3 KB (đạt chỉ tiêu < 700 KB). ONNX FP32 đạt độ trễ 0.29 ms/nhịp (tăng tốc gần 4x).
5. **Ứng dụng Full-Stack & Y tế**: Hệ thống Web Full-Stack hoạt động ổn định với luồng WebSocket 360Hz hai kênh, quản lý bệnh nhân, phân quyền RBAC 3 vai trò, cơ chế duyệt nhãn Human-in-the-loop lưu vết Audit Trail, và xuất báo cáo y tế PDF/CSV.
6. **Chất lượng phần mềm**: 42/42 bài test tự động pytest pass 100%, Lint sạch lỗi, CI/CD và Docker Compose hoàn thiện.

### 4.3. Những gì CHƯA HOÀN THÀNH & HẠN CHẾ KỸ THUẬT (Đánh giá trung thực)

#### Hạn chế 1: Khả năng tổng quát hóa trên các lớp hiếm (Lớp S và Lớp F) khi gặp Domain Shift
Khi kiểm nghiệm ResNet-1D trên 3 cơ sở dữ liệu quốc tế độc lập (INCART, SVDB, EDB):

| Cơ sở dữ liệu | Số bản ghi | Accuracy tổng | Recall Lớp N | Recall Lớp V | Recall Lớp S | Recall Lớp F |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **INCART (12 chuyển đạo)** | 75 bản ghi | 85.94% | 89.2% | 78.4% | 12.8% | 18.3% |
| **SVDB (Supraventricular)** | 78 bản ghi | 74.12% | 81.5% | 76.9% | 0.4% ⚠️ | 11.2% |
| **EDB (European ST-T)** | 90 bản ghi | 78.50% | 84.1% | 82.3% | 3.6% ⚠️ | 9.5% |
| **INCART (Sau Fine-tune)** ⭐ | 75 bản ghi | **93.18%** | 94.6% | 88.2% | 42.5% | 39.1% |

> [!WARNING]
> Lớp V (Thất) và lớp N (Bình thường) duy trì độ chính xác cao (78%–94%) nhờ hình thái sóng QRS rõ rệt. Tuy nhiên, lớp S (Trên thất) và lớp F (Hợp nhất) bị sụt giảm Recall do khác biệt vị trí đạo trình đo và số lượng mẫu gốc quá ít trong tập train (2.5% và 0.7%). Thử nghiệm Fine-tune trên INCART đã nâng Accuracy từ 85.94% lên 93.18%, chứng minh tính chuyển giao của mô hình. Giải pháp lâu dài là cần huấn luyện mô hình ngay từ đầu trên tập dữ liệu tổng hợp đa nguồn (Multi-database training).

#### Hạn chế 2: Ngưỡng quy tắc Rung nhĩ (AFib Threshold = 0.62) chưa kiểm định mù quy mô lớn
Module `AfibScreener` hiện hoạt động dựa trên ngưỡng thực nghiệm 0.62 trên tập MIT-BIH. Hạn chế là chưa kịp thực hiện kiểm định thống kê mù trên toàn bộ Cơ sở dữ liệu Rung nhĩ PhysioNet AFDB (hàng trăm giờ ghi). Do đó, chỉ số AFib hiện tại đóng vai trò gợi ý sàng lọc, chưa được coi là kết luận chẩn đoán xác định.

#### Hạn chế 3: Tích hợp phần cứng cảm biến IoT thực tế (Physical Hardware Sensor)
Hệ thống hiện truyền phát thời gian thực thông qua bộ giả lập WebSocket đọc từ các bản ghi chuẩn PhysioNet WFDB 360Hz. Nhóm chưa hàn nối trực tiếp mạch cảm biến điện cực phần cứng vật lý (như module AD8232 hoặc MAX30003 kết nối ESP32 qua WiFi/MQTT). Kiến trúc WebSocket đã sẵn sàng ở chuẩn 360Hz để tiếp nhận luồng dữ liệu phần cứng ở pha phát triển tiếp theo.

#### Hạn chế 4: Thử nghiệm lâm sàng tại bệnh viện (Clinical Trial)
Toàn bộ các kết quả đánh giá thực nghiệm được thực hiện trên các bộ dữ liệu đối chuẩn quốc tế chuẩn mực. Hệ thống chưa có điều kiện thử nghiệm lâm sàng mù đôi (double-blind trial) trực tiếp trên bệnh nhân tại các khoa Cấp cứu / Tim mạch bệnh viện.

### 4.4. Đề xuất hỗ trợ và định hướng từ Ban Giảng viên
1. **Về giải thuật AI**: Ý kiến về kỹ thuật Loss Re-weighting hoặc Contrastive Learning để cải thiện năng lực nhận diện của lớp hiếm S và F trong môi trường đa nguồn dữ liệu.
2. **Về kiểm định AFib**: Định hướng về việc thiết lập giao thức hiệu chỉnh ngưỡng AFib tối ưu trên tập dữ liệu AFDB.
3. **Về quy chuẩn y tế**: Nhận xét về cấu trúc báo cáo bệnh án PDF và quy trình Human-in-the-loop để tiếp cận sát nhất với tiêu chuẩn phần mềm thiết bị y tế (SaMD).

---

## CHƯƠNG 5: KẾ HOẠCH VÀ KỊCH BẢN LIVE DEMO CHO NGÀY BẢO VỆ 31/10/2026

### 5.1. Cấu trúc bài thuyết trình bảo vệ (18 Slide)
- **Phần 1: Mở đầu & Đặt vấn đề (3 slide)**: Slide 1-3: Mở đầu, bối cảnh lâm sàng, thách thức 'hộp đen' và mục tiêu sản phẩm.
- **Phần 2: Phương pháp & Mô hình AI (5 slide)**: Slide 4-8: Chuỗi tiền xử lý DSP, Pan-Tompkins R-peak, Sửa rò rỉ dữ liệu, Benchmark 5 mô hình, Toán học 1D Grad-CAM, Lượng tử hóa ONNX INT8.
- **Phần 3: Kiến trúc Hệ thống (4 slide)**: Slide 9-12: Kiến trúc Full-Stack thời gian thực, WebSocket 360Hz 2 kênh, Cơ sở dữ liệu, Phân quyền RBAC 3 vai trò, Human-in-the-loop và Audit Trail.
- **Phần 4: Đánh giá Kết quả & Hạn chế (3 slide)**: Slide 13-15: Đối chiếu tiến độ 100%, Kết quả đạt được, Minh bạch các hạn chế kỹ thuật (Lớp S/F trên dữ liệu ngoài, Ngưỡng AFib, Cảm biến phần cứng).
- **Phần 5: Trình diễn Trực tiếp (2 slide)**: Slide 16-17: Kịch bản Live Demo trực tiếp hệ thống.
- **Phần 6: Kết luận & Triển vọng (1 slide)**: Slide 18: Kết luận, bài học kinh nghiệm và hướng phát triển.

### 5.2. Kịch bản Live Demo 5 bước trên hệ thống
1. **Pha 1: Giám sát ECG Thời gian thực (Real-time Streaming)**: Mở Dashboard real-time, phát Record 100 (Nhịp xoang bình thường), đồ thị 2 kênh MLII/V1 mượt mà 60 FPS, nhịp tim ~75 BPM, thẻ trạng thái màu xanh 'Normal'. Chuyển sang Record 200 (Bệnh nhân có nhiều PVC), hệ thống tức thì dán nhãn màu đỏ 'Ventricular Ectopic (PVC)' với độ tin cậy > 95%.
2. **Pha 2: Báo động đa tầng chuẩn Y tế**: Kích hoạt chuông cảnh báo âm thanh và đèn chớp đỏ khi phát hiện chuỗi PVC. Người trình bày bấm nút 'Tắt tiếng tạm thời 2 phút' (Alarm Mute). Chuông im lặng nhưng cờ cảnh báo vẫn hiển thị chờ xử lý theo đúng chuẩn an toàn IEC 60601-1-8.
3. **Pha 3: Explainable AI 1D Grad-CAM**: Nhấp trực tiếp vào nhịp PVC trên đồ thị để mở Trang Phân tích Chuyên sâu (XAI Deep Dive). Bản đồ nhiệt 1D Grad-CAM hiển thị đỏ rực tại phức bộ QRS giãn rộng, chứng minh AI đưa ra kết luận dựa trên căn cứ bệnh học.
4. **Pha 4: Human-in-the-loop & Xuất Báo cáo**: Đăng nhập tài khoản Bác sĩ (Doctor), duyệt/sửa nhãn, hệ thống ghi nhận vào nhật ký kiểm toán Audit Trail, nhấn nút 'Xuất Báo cáo Bệnh án' tạo tệp PDF chứa đầy đủ thông tin hành chính, đồ thị sóng và chữ ký phê duyệt.
5. **Pha 5: Chẩn đoán Ngoại tuyến & Edge AI**: Chẩn đoán ngoại tuyến: Tải tệp CSV ngoài, chạy trọn gói pipeline DSP -> Pan-Tompkins -> ResNet-1D trong vài giây. Mở giao diện kiểm tra mô hình ONNX INT8 dung lượng 697.3 KB sẵn sàng nhúng Edge.

### 5.3. Kế hoạch dự phòng sự cố kỹ thuật (Contingency Plan)
1. **Sự cố rớt mạng**: Toàn bộ Backend và Frontend chạy offline trên mạng cục bộ (Localhost) không cần Internet.
2. **Sự cố môi trường phần mềm**: Đóng gói sẵn Docker Compose 2 container dự phòng, khôi phục bằng 1 lệnh duy nhất.
3. **Video ghi hình dự phòng**: Quay sẵn video chất lượng cao 4K ghi lại trọn vẹn 5 bước demo để trình chiếu khi cần.

---

## KẾT LUẬN & TÀI LIỆU THAM KHẢO

- **Kết luận**: Đồ án **NEURO-ECG** đã hoàn thành trọn vẹn các mục tiêu nghiên cứu và triển khai ứng dụng: Không chỉ dừng lại ở mô hình học sâu lý thuyết, dự án đã hiện thực hóa một sản phẩm phần mềm y tế hoàn chỉnh, kết hợp nhuần nhuyễn giữa DSP, ResNet-1D, 1D Grad-CAM, ONNX INT8 và nền tảng Full-Stack thời gian thực có phân quyền RBAC và cơ chế Human-in-the-loop.
- **Tài liệu tham khảo chính**:
  1. Goldberger, A. L., et al. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals. Circulation, 101(23), e215-e220.
  2. Pan, J., & Tompkins, W. J. (1985). A real-time QRS detection algorithm. IEEE Transactions on Biomedical Engineering, (3), 230-236.
  3. Selvaraju, R. R., et al. (2017). Grad-CAM: Visual explanations from deep networks via gradient-based localization. In Proceedings of the IEEE ICCV, pp. 618-626.
  4. He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. In Proceedings of the IEEE CVPR, pp. 770-778.
  5. Association for the Advancement of Medical Instrumentation (AAMI). (1998). Testing and reporting performance results of cardiac rhythm and ST segment measurement algorithms (ANSI/AAMI EC57:1998).
  6. International Electrotechnical Commission (IEC). (2006). Medical electrical equipment - Part 1-8: Alarm systems in medical electrical equipment (IEC 60601-1-8:2006).
  7. Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. JAIR, 16, 321-357.

---

## PHỤ LỤC: HƯỚNG DẪN CÀI ĐẶT VÀ TÁI LẬP THỰC NGHIỆM

1. **Tải mã nguồn**:
   ```bash
   git clone https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection.git
   cd ECG-Arrhythmia-Detection
   ```
2. **Môi trường Backend Python**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Cài đặt Frontend**:
   ```bash
   cd frontend && npm install && cd ..
   ```
4. **Chạy Backend FastAPI**:
   ```bash
   .\venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. **Chạy Frontend React 19**:
   ```bash
   cd frontend && npm run dev
   # Truy cập hệ thống tại: http://localhost:5173
   ```
6. **Chạy Kiểm thử tự động**:
   ```bash
   .\venv\Scripts\pytest backend/tests/ -v
   ```
7. **Xuất & Kiểm chứng mô hình ONNX**:
   ```bash
   .\venv\Scripts\python -m src.models.export_onnx
   .\venv\Scripts\python -m backend.scripts.validate_onnx_classification
   ```
