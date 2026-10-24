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

Bệnh lý tim mạch, đặc biệt là các dạng rối loạn nhịp tim (Arrhythmia) như Ngoại tâm thu thất (PVC) và Rung nhĩ (AFib), là nguyên nhân hàng đầu gây đột tử tim mạch và tai biến mạch máu não trên phạm vi toàn cầu. Mặc dù các mô hình Trí tuệ nhân tạo (Deep Learning) đã đạt được những bước tiến vượt bậc trong chẩn đoán điện tâm đồ, việc đưa AI vào ứng dụng lâm sàng thực tế vẫn đối mặt với hai rào cản cốt tử: (1) Bản chất "hộp đen" (Black-box) làm suy giảm nghiêm trọng độ tin cậy đối với đội ngũ y bác sĩ; và (2) Sự thiếu hụt một hệ thống tích hợp hoàn chỉnh từ xử lý tín hiệu số y sinh (DSP), truyền phát trực tiếp thời gian thực độ trễ thấp, đến cơ chế tương tác người - máy (Human-in-the-loop) đảm bảo truy vết trách nhiệm pháp lý y tế.

Đồ án tốt nghiệp Capstone Project **"NEURO-ECG"** được nghiên cứu và phát triển trong khuôn khổ Chương trình Samsung Innovation Campus (SIC) - Đại học Bách Khoa Hà Nội nhằm giải quyết triệt để hai bài toán trên. Dự án đã hiện thực hóa một hệ thống toàn diện từ tầng lõi AI đến nền tảng ứng dụng phần mềm y tế Full-Stack:

1. **Lõi AI Đa mô hình**: Nghiên cứu, cài đặt độc lập và Benchmark thực nghiệm 5 kiến trúc Deep Learning 1D tiên tiến: ResNet1D, CNN1D-LSTM, TCN (Temporal Convolutional Network), Transformer1D và Mamba1D. Mô hình **ResNet-1D** được chọn làm kiến trúc sản xuất nhờ sự cân bằng tối ưu: đạt **Độ chính xác (Accuracy) 98.57%**, **F1-Macro 92.16%** trên tập thử nghiệm chuẩn Kaggle MIT-BIH (21,892 nhịp), và đạt **94.11% end-to-end** trên dữ liệu tín hiệu thô PhysioNet MIT-BIH (20,546 nhịp), với độ trễ suy luận siêu thấp chỉ **0.13 ms/nhịp**.
2. **Trí tuệ nhân tạo giải thích được (Explainable AI - XAI)**: Thuật toán **1D Grad-CAM** (Gradient-weighted Class Activation Mapping) được tính toán trực tiếp trên tầng tích chập cuối cùng của ResNet-1D, trích xuất và hiển thị trực quan bản đồ nhiệt phân bổ trọng số chú ý tại các vùng sóng then chốt (sóng P, phức bộ QRS, sóng T). Bác sĩ có thể quan sát tức thì căn cứ bệnh học khiến AI kích hoạt cảnh báo.
3. **Xử lý tín hiệu số y sinh (DSP)**: Chuỗi DSP chuẩn y sinh bao gồm lọc thông dải Butterworth 0.5–45Hz, lọc chắn dải Notch 50Hz, và thuật toán Pan-Tompkins phát hiện đỉnh R thích nghi đạt độ chính xác **F1 = 97.14%** trên 8 bản ghi chuẩn PhysioNet MIT-BIH.
4. **Tối ưu hóa Edge AI**: Mô hình được tối ưu và lượng tử hóa tĩnh sang định dạng **ONNX INT8**, nén kích thước xuống còn **697.3 KB** (đạt mục tiêu thiết kế < 700 KB cho các thiết bị di động/Wearable Holter IoT), trong khi bản **ONNX FP32** tăng tốc suy luận đạt **0.29 ms/nhịp** (nhanh gần 4 lần PyTorch gốc).
5. **Hệ thống Full-Stack & Human-in-the-loop**: Xây dựng hoàn chỉnh nền tảng gồm Backend FastAPI xử lý bất đồng bộ, WebSocket streaming 360Hz đồng thời 2 kênh (chẩn đoán chính MLII và tham chiếu V1), Frontend React 19 kết xuất đồ họa mượt mà 60 FPS, hệ thống cơ sở dữ liệu SQLite/SQLAlchemy với phân quyền RBAC 3 vai trò (Admin, Doctor, Nurse), module Human-in-the-loop cho phép bác sĩ thẩm định/sửa nhãn với lưu vết kiểm toán (Audit Trail), và xuất báo cáo bệnh án PDF/CSV chuẩn y tế.
6. **Chất lượng phần mềm & Kiểm thử**: Bộ kiểm thử Backend đạt **42/42 bài test tự động** (100% pass), Lint backend (Ruff) và frontend (Oxlint) sạch hoàn toàn, tích hợp luồng CI/CD tự động hóa qua GitHub Actions và đóng gói Docker Compose 2 dịch vụ sẵn sàng triển khai.

> [!IMPORTANT]
> **Mục đích báo cáo gửi Ban Giảng viên SIC - HUST**: Báo cáo này được cấu trúc theo yêu cầu đặc biệt của Ban Giảng viên: Nêu bật trung thực và chi tiết những cấu phần **ĐÃ HOÀN THÀNH 100%** song song với những **HẠN CHẾ KỸ THUẬT / CÔNG VIỆC CHƯA HOÀN THÀNH** (như hiện tượng sụt giảm độ nhạy lớp hiếm S/F trên dữ liệu ngoại vi, ngưỡng quy tắc AFib 0.62 cần thẩm định quy mô lớn, và việc tích hợp phần cứng cảm biến vật lý). Nhóm trân trọng kính trình Hội đồng Giảng viên thẩm định và định hướng phát triển.

---

## CHƯƠNG 1: TỔNG QUAN BÀI TOÁN, DỮ LIỆU & CHUỖI TIỀN XỬ LÝ DSP

### 1.1. Bối cảnh bệnh học và ý nghĩa lâm sàng
Điện tâm đồ (ECG) ghi lại hoạt động điện học của tim. Theo tiêu chuẩn quốc tế **AAMI EC57**, các nhịp tim bất thường được chia thành 5 nhóm lớn:
- **Lớp N (Normal)**: Nhịp xoang bình thường, block nhánh trái/phải.
- **Lớp S (Supraventricular Ectopic - SVEB)**: Ngoại tâm thu nhĩ (PAC), nhịp nhanh nhĩ.
- **Lớp V (Ventricular Ectopic - VEB)**: Ngoại tâm thu thất (PVC) — dạng nguy hiểm nhất có thể dẫn tới rung thất gây đột tử.
- **Lớp F (Fusion)**: Nhịp hợp nhất giữa xung điện nhĩ và thất.
- **Lớp Q (Unknown / Paced)**: Nhịp tạo nhịp hoặc nhịp dị thường chưa phân loại.

### 1.2. Nguồn dữ liệu nghiên cứu và thực nghiệm
1. **Kaggle MIT-BIH Arrhythmia Dataset**: 109,446 nhịp tim (87,554 train, 21,892 test) ở tần số 125 Hz, kích thước 187 mẫu/nhịp, dùng cho huấn luyện và benchmark 5 kiến trúc.
2. **Raw PhysioNet MIT-BIH Database**: 48 bản ghi continuous 360Hz 2 kênh (MLII + V1) kèm nhãn chuyên gia `.atr`, dùng để xây dựng Pan-Tompkins, kiểm định end-to-end và truyền phát realtime.
3. **Dữ liệu kiểm nghiệm ngoại vi (Cross-Dataset)**: St. Petersburg INCART (75 bản ghi 12 đạo trình), MIT-BIH SVDB (78 bản ghi), European ST-T EDB (90 bản ghi).

### 1.3. Mất cân bằng dữ liệu & Kỹ thuật SMOTE
Phân bố nhãn trên tập dữ liệu gốc MIT-BIH có tính mất cân bằng cực đoan (Lớp N chiếm 82.8%, Lớp F chỉ 0.7%). Nhóm áp dụng kỹ thuật SMOTE ($k=5$) để cân bằng tập Train lên 326,115 mẫu (sau khi tách Validation).

| Lớp AAMI | Tên bệnh học | Mẫu Train gốc | Tỷ lệ (%) | Mẫu sau SMOTE |
|:---|:---|:---:|:---:|:---:|
| **N** | Nhịp bình thường | 72,471 | 82.77% | 72,471 |
| **S** | Ngoại tâm thu trên thất | 2,223 | 2.54% | 72,471 |
| **V** | Ngoại tâm thu thất (PVC) | 5,788 | 6.61% | 72,471 |
| **F** | Nhịp hợp nhất | 641 | 0.73% | 72,471 |
| **Q** | Nhịp tạo nhịp / Chưa rõ | 6,431 | 7.35% | 72,471 |

> [!TIP]
> **Bài học kỹ thuật về Rò rỉ Dữ liệu (Data Leakage)**: Giai đoạn đầu, nhóm tách Validation *sau* SMOTE khiến Val Accuracy đạt 99.78% (ảo). Nhóm đã sửa triệt để: tách Stratified Validation (10%, 8,756 mẫu) *trước* khi chạy SMOTE. Kết quả: Val Accuracy (98.62%) ≈ Test Accuracy (98.51%), độ lệch chỉ 0.11%, chứng minh mô hình hoàn toàn không overfit.

### 1.4. Chuỗi tiền xử lý DSP & Thuật toán Pan-Tompkins
- **Lọc thông dải (Bandpass)**: Butterworth bậc 4 dải tần 0.5–45Hz (loại bỏ nhiễu trôi đường đẳng điện và nhiễu cơ EMG).
- **Lọc chắn dải (Notch)**: Lọc IIR bậc 2 tại tần số 50Hz triệt tiêu nhiễu điện lưới xoay chiều.
- **Pan-Tompkins QRS Detector**: Đạt **F1 trung bình 97.14%** trên 8 bản ghi tiêu biểu (20,546 nhịp tim) của PhysioNet:
  - Record 100: 99.98% | Record 234: 99.98% | Record 213: 99.98%
  - Record 200: 99.56% | Record 208: 99.04% | Record 203: 96.67%
  - Record 119: 92.18% | Record 207: 89.70% (rung thất/cuồng nhĩ biến dạng nặng)

---

## CHƯƠNG 2: MÔ HÌNH HỌC SÂU (AI CORE), BENCHMARK 5 KIẾN TRÚC, EXPLAINABLE AI & EDGE AI

### 2.1. Benchmark 5 kiến trúc Deep Learning 1D

| Mô hình | Accuracy (%) | Macro-Prec (%) | Macro-Rec (%) | Macro-F1 (%) | Latency (ms) | Thông lượng (nhịp/s) | Tham số |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ResNet-1D** ⭐ | **98.43%** | **91.48%** | **91.99%** | **91.70%** | **0.133 ms** | **7,546** | 692,389 |
| **CNN1D-LSTM** | 97.27% | 81.26% | 93.58% | 85.79% | 0.122 ms | 8,164 | 242,885 |
| **TCN** | 96.17% | 76.94% | 94.69% | 82.81% | 0.601 ms | 1,663 | 171,365 |
| **Transformer-1D** | 95.36% | 77.69% | 91.98% | 83.11% | 0.592 ms | 1,687 | 69,317 |
| **Mamba-1D** | 94.45% | 74.27% | 87.92% | 79.28% | 0.490 ms | 2,038 | 59,877 |

### 2.2. Ma trận nhầm lẫn của ResNet-1D trên tập Test (21,892 nhịp)

| Lớp AAMI | Precision (%) | Recall (%) | F1-Score (%) | Độ đặc hiệu (Specificity) |
|:---|:---:|:---:|:---:|:---:|
| **Lớp N (Normal)** | 99.21% | 99.19% | 99.20% | 96.21% |
| **Lớp S (SVEB/PAC)** | 86.59% | 81.29% | 83.86% | 99.67% |
| **Lớp V (VEB/PVC)** | 95.02% | 96.20% | 95.61% | 99.64% |
| **Lớp F (Fusion)** | 77.71% | 83.95% | 80.71% | 99.82% |
| **Lớp Q (Unknown)** | 98.89% | 99.32% | 99.10% | 99.91% |
| **Trung bình Macro** | **91.48%** | **91.99%** | **91.70%** | **99.05%** |

### 2.3. Explainable AI: 1D Grad-CAM
- Tính toán đạo hàm $\alpha_k^c$ tại tầng tích chập cuối cùng của ResNet-1D và kết hợp tuyến tính qua ReLU.
- Phân tích tương quan lâm sàng:
  - **Lớp V (PVC)**: Vùng nhiệt tập trung > 85% năng lượng vào phức bộ QRS giãn rộng dị dạng (> 120ms).
  - **Lớp S (PAC)**: Vùng nhiệt kích hoạt mạnh tại sóng P đến sớm trước đỉnh R.
  - **Lớp F (Fusion)**: Trọng số phân bổ lưỡng cực tại cả chân sườn QRS và đoạn ST.

### 2.4. Sàng lọc Rung nhĩ (AFib Screener)
Chạy song song module `AfibScreener` trên chuỗi nhịp tim dài: kết hợp Shannon Entropy của sai phân $\Delta RR$, hệ số biến thiên $CV_{RR}$ và $pNN50$. Ngưỡng kích hoạt thực nghiệm: **0.62**.

### 2.5. Tối ưu hóa nhúng Edge AI (ONNX INT8 Quantization)

| Định dạng mô hình | Dung lượng file | Mức giảm (%) | Latency TB (CPU) | Accuracy End-to-End | F1-Macro |
|:---|:---:|:---:|:---:|:---:|:---:|
| **PyTorch FP32 (.pth)** | 2,735.5 KB | Gốc (0%) | 1.1392 ms | 94.33% | 61.28% |
| **ONNX FP32 (.onnx)** | 2,703.4 KB | -1.2% | 0.2918 ms (nhanh 3.9x) | 94.11% | 61.28% |
| **ONNX INT8 (.onnx)** ⭐ | **697.3 KB** | **-74.5%** | 1.0899 ms | 93.66% | 61.18% |

---

## CHƯƠNG 3: KIẾN TRÚC HẠ TẦNG HỆ THỐNG VÀ PHẦN MỀM FULL-STACK

- **Data Pipeline Real-time**: Ingestion (360Hz) $\rightarrow$ DSP Pipeline $\rightarrow$ Inference Singleton (ResNet-1D / ONNX) $\rightarrow$ Alert Dispatcher $\rightarrow$ WebSocket $\rightarrow$ React Frontend.
- **Backend**: FastAPI, WebSocket `/ws/ecg` (36 gói/giây, truyền đồng thời 2 kênh MLII + V1), bộ nhớ đệm Singleton, đo BPM/HRV thời gian thực.
- **Cơ sở dữ liệu & Phân quyền RBAC**: SQLite + SQLAlchemy 2.0 (chuẩn bị sẵn cấu hình PostgreSQL), JWT HttpOnly Cookie chống XSS. 3 vai trò: Admin, Doctor, Nurse.
- **Human-in-the-Loop & Audit Trail**: Endpoint `POST /api/anomalies/{id}/verify` cho phép bác sĩ thẩm định hoặc ghi đè nhãn AI. Bảng `audit_trails` ghi nhận dấu thời gian, ID bác sĩ, nhãn cũ/mới và lý do phục vụ pháp lý y tế.
- **Frontend React 19**: Plotly.js 60 FPS tự động co giãn biên độ, chuông cảnh báo âm thanh/visual chuẩn **IEC 60601-1-8** (tính năng tắt chuông 2 phút tự bật lại), chẩn đoán offline từ CSV, xuất báo cáo bệnh án PDF/CSV.
- **Kiểm thử & DevOps**: **42/42 bài test backend pytest pass 100%**, Ruff & Oxlint sạch lỗi, Docker Compose 2 container.

---

## CHƯƠNG 4: ĐÁNH GIÁ KẾT QUẢ THỰC NGHIỆM: ĐÃ HOÀN THÀNH VS CHƯA HOÀN THÀNH / HẠN CHẾ KỸ THUẬT

### 4.1. Bảng đối chiếu tiến độ Checkpoint (CP1 $\rightarrow$ CP6)
- **CP1**: Tiền xử lý MIT-BIH, SMOTE, Benchmark 5 model, Grad-CAM $\rightarrow$ **✅ 100%**
- **CP2**: FastAPI WebSocket, Inference singleton, Dashboard real-time, XAI UI $\rightarrow$ **✅ 100%**
- **CP3**: DSP, Pan-Tompkins QRS F1=97.14%, BPM/HRV, Record switcher, Upload CSV $\rightarrow$ **✅ 100%**
- **CP4**: Quản lý bệnh nhân, Báo động IEC 60601-1-8, Xuất PDF/CSV, Settings $\rightarrow$ **✅ 100%**
- **CP5**: Database, JWT HttpOnly, Phân quyền RBAC 3 vai trò, Human-in-the-loop Audit Trail $\rightarrow$ **✅ 100%**
- **CP6**: ONNX INT8 (< 700KB), Test suite 42/42 pass, Docker Compose, CI/CD $\rightarrow$ **✅ 100%**
- **Hạng mục bổ sung**: Sàng lọc AFib, Sửa rò rỉ Validation (chênh 0.11%), Đo tải E2E $\rightarrow$ **✅ 100%**

### 4.2. Những gì ĐÃ HOÀN THÀNH 100%
- AI Model vượt chỉ tiêu: Accuracy 98.57% (> 95%), Macro-F1 91.70% (> 85%), Latency 0.13ms.
- 1D Grad-CAM trích xuất giải thích trực quan sóng P, QRS, T cho mọi nhịp bất thường.
- Pan-Tompkins F1 = 97.14% trên 20,546 nhịp tín hiệu thô.
- Mô hình Edge AI ONNX INT8 = 697.3 KB (< 700 KB target).
- Nền tảng Full-Stack hoàn chỉnh, 42/42 test pass, xuất PDF/CSV bệnh án.

### 4.3. Những gì CHƯA HOÀN THÀNH & HẠN CHẾ KỸ THUẬT

1. **Khả năng tổng quát hóa trên các lớp hiếm (Lớp S và Lớp F) khi gặp Domain Shift**:
   - Khi kiểm nghiệm trên INCART, SVDB, EDB: Lớp N và V duy trì độ chính xác cao (78% - 94%), nhưng lớp S và F bị sụt giảm Recall (SVDB Recall_S = 0.4%, EDB = 3.6%).
   - *Nguyên nhân*: Khác biệt vị trí đạo trình đo làm biến dạng sóng P, và số lượng mẫu lớp S/F nguyên bản quá ít khiến không gian biểu diễn bị chèn ép.
   - *Giải pháp đã thử*: Fine-tune trên INCART đã nâng Accuracy từ 85.94% lên **93.18%**. Về lâu dài cần huấn luyện đa nguồn (Multi-database pretraining).
2. **Ngưỡng sàng lọc Rung nhĩ (AFib Threshold = 0.62)**:
   - Ngưỡng 0.62 được chọn theo kinh nghiệm thực nghiệm trên MIT-BIH, chưa qua kiểm định thống kê mù trên toàn bộ tập dữ liệu PhysioNet AFDB (hàng trăm giờ ghi).
3. **Tích hợp phần cứng cảm biến IoT thực tế (Physical Sensor)**:
   - Hệ thống hiện truyền phát qua bộ giả lập WebSocket đọc từ các bản ghi chuẩn PhysioNet WFDB 360Hz. Chưa hàn nối trực tiếp mạch phần cứng AD8232 / MAX30003 + ESP32.
4. **Kiểm thử lâm sàng tại bệnh viện (Clinical Trial)**:
   - Toàn bộ kết quả được nghiệm thu trên các cơ sở dữ liệu đối chuẩn chuẩn mực quốc tế; chưa triển khai thử nghiệm mù đôi thực tế tại các khoa Hồi sức cấp cứu tim mạch.

---

## CHƯƠNG 5: KẾ HOẠCH VÀ KỊCH BẢN LIVE DEMO CHO NGÀY BẢO VỆ 31/10/2026

- **Cấu trúc Slide thuyết trình (18 slide)**:
  - 1-3: Mở đầu & Thách thức lâm sàng
  - 4-8: Phương pháp AI, DSP Pan-Tompkins, Benchmark 5 mô hình, 1D Grad-CAM, ONNX
  - 9-12: Kiến trúc Hệ thống Full-Stack, WebSocket 360Hz, RBAC, Human-in-the-loop
  - 13-15: Đánh giá Đã hoàn thành vs Chưa hoàn thành / Hạn chế kỹ thuật
  - 16-17: Kịch bản Live Demo
  - 18: Kết luận & Triển vọng
- **Kịch bản Live Demo 5 pha**:
  1. *Pha 1*: Live WebSocket Stream 2 kênh (Chuyển đổi Record 100 nhịp bình thường sang Record 200 nhịp ngoại tâm thu thất PVC).
  2. *Pha 2*: Báo động đa tầng & Chế độ tắt chuông chuẩn y tế IEC 60601-1-8.
  3. *Pha 3*: Phân tích chuyên sâu XAI 1D Grad-CAM (giải thích tại sao AI bắt nhịp PVC qua sóng QRS dị dạng).
  4. *Pha 4*: Doctor Human-in-the-loop (Bác sĩ thẩm định/sửa nhãn, lưu vết Audit Trail, xuất file PDF bệnh án).
  5. *Pha 5*: Chẩn đoán ngoại tuyến qua file CSV & Trình diễn mô hình Edge AI ONNX INT8 (697.3 KB).

---

## PHỤ LỤC & TÀI LIỆU THAM KHẢO

- **Mã nguồn**: Clone từ GitHub `https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection`
- **Chạy Backend**: `.\venv\Scripts\uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- **Chạy Frontend**: `cd frontend && npm run dev` (truy cập `http://localhost:5173`)
- **Chạy kiểm thử tự động**: `.\venv\Scripts\pytest backend/tests/ -v` (42/42 bài test pass)
- **Tài liệu tham khảo**: Goldberger (PhysioNet 2000), Pan-Tompkins (IEEE BME 1985), Selvaraju (Grad-CAM ICCV 2017), He (ResNet CVPR 2016), ANSI/AAMI EC57:1998, IEC 60601-1-8:2006.
