# DÀN Ý SLIDE BẢO VỆ CAPSTONE PROJECT THEO CHUẨN TEMPLATE SAMSUNG SIC
## CHƯƠNG TRÌNH SAMSUNG INNOVATION CAMPUS (SIC) 2026 — ĐẠI HỌC BÁCH KHOA HÀ NỘI

**ĐỀ TÀI**: **HỆ THỐNG GIÁM SÁT ECG THỜI GIAN THỰC TÍCH HỢP TRÍ TUỆ NHÂN TẠO GIẢI THÍCH ĐƯỢC (EXPLAINABLE AI) VÀ HỖ TRỢ CHẨN ĐOÁN RỐI LOẠN NHỊP TIM ĐA TẦNG (NEURO-ECG)**  
- **Nhóm thực hiện**: Nguyễn Đào Nam Hải (Team Leader) · Phan Thị Hải Yến (Member)  
- **Ngày bảo vệ chính thức**: 31/10/2026  
- **Tệp Word chi tiết**: [`docs/Dan_y_va_Huong_dan_Slide_Thuyet_trinh_SIC.docx`](Dan_y_va_Huong_dan_Slide_Thuyet_trinh_SIC.docx)  
- **Mã nguồn dự án**: [https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection](https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection)

---

## I. BẢNG CHIẾN LƯỢC ĐỐI CHUẨN THANG ĐIỂM 100 CỦA SAMSUNG SIC

Dàn ý slide này được tái cấu trúc hoàn toàn dựa trên **Template chính thức của Samsung Innovation Campus** (gồm 5 Unit: *Introduction*, *Project Execution*, *Results*, *Projected Impact*, *Team Review & Comments*) và đối chuẩn trực tiếp với **Thang điểm 100 của Hội đồng Giảng viên SIC**:

| Tiêu chí đánh giá của SIC | Tỷ trọng | Trọng tâm cần thể hiện trên Slide | Slide tương ứng |
|:---|:---:|:---|:---:|
| **1. Tính hoàn chỉnh của sản phẩm** | **30%** | Sản phẩm chạy thực tế, không dừng ở mô hình lý thuyết: WebSocket 360Hz, React 19 Plotly, SQLite/RBAC, 42/42 tests pass, Live Demo 5 pha. | Slide 5, 9, 10, 11, 12, 13, 14 |
| **2. Tính sáng tạo & Ứng dụng thực tế** | **25%** | Explainable AI (1D Grad-CAM) giải quyết "hộp đen" y tế; Lượng tử hóa ONNX INT8 (697 KB) cho Edge AI Wearable; Chuẩn an toàn báo động IEC 60601-1-8. | Slide 2, 3, 7, 8, 12, 15 |
| **3. Kỹ năng làm việc nhóm & Tiến độ WBS** | **15%** | Bảng phân vai rõ ràng giữa Nam Hải và Hải Yến; Tiến độ WBS hoàn thành qua 6 Checkpoint có ghi nhận đóng góp minh bạch. | Slide 4, 17 |
| **4. Trình bày – Thuyết trình – Slide/Báo cáo** | **20%** | Slide chuẩn khung 5 Unit của Samsung SIC, trực quan, nhúng đúng 9 biểu đồ thực nghiệm, thuyết trình mạch lạc, tự tin. | Toàn bộ 18 slide |
| **5. Phản biện và trả lời câu hỏi** | **10%** | Nắm vững bản chất kỹ thuật, trung thực chỉ rõ hạn chế Domain Shift lớp S/F và bảo vệ giải pháp một cách khoa học. | Slide 14, 16, 18 & Bộ Q&A |

---

## II. DÀN Ý CHI TIẾT 18 SLIDE THEO KHUNG TEMPLATE SAMSUNG SIC

### UNIT 1. INTRODUCTION (Tổng Quan Đề Tài & Kế Hoạch Nhóm)

#### SLIDE 1: TITLE SLIDE (Project Name & Team Info)
- 🏷️ **Khung Template SIC**: *Template Header: Project Title & Team Info*
- 🎯 **Mục tiêu đánh giá**: Tạo ấn tượng trang trọng, khoa học công nghệ, chuẩn nhận diện Samsung Innovation Campus & HUST.
- **Nội dung hiển thị trên slide**:
  - Project Title: **REAL-TIME EXPLAINABLE AI ECG ARRHYTHMIA MONITORING & CLINICAL DECISION SUPPORT SYSTEM (NEURO-ECG)**
  - Team Name / Members: Nguyễn Đào Nam Hải (Team Leader) · Phan Thị Hải Yến (Member)
  - Course: Samsung Innovation Campus (SIC) - HUST AI Track 2026
  - Repository: `https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection`
- 🎨 **Hình vẽ / Biểu đồ chèn**: Logo HUST và Logo Samsung đặt 2 góc trên; hình nền phẳng tối giản (Deep Navy `#1E3A8A`) có đường sóng ECG chạy ngang mờ.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Kính thưa Hội đồng Giảng viên Samsung Innovation Campus và các Thầy Cô giáo ĐH Bách Khoa Hà Nội, hôm nay nhóm chúng em xin được báo cáo đề tài Capstone Project: Hệ thống giám sát ECG thời gian thực tích hợp Explainable AI..."*

#### SLIDE 2: 1.1. BACKGROUND INFORMATION (Bối Cảnh & Thách Thức Thực Tiễn)
- 🏷️ **Khung Template SIC**: *Template Unit 1.1: Background Information*
- 🎯 **Mục tiêu đánh giá**: Làm nổi bật bài toán thực tiễn và 2 rào cản cốt tử khi ứng dụng AI vào lâm sàng y tế (Nhắm vào 25% điểm Tính thực tiễn).
- **Nội dung hiển thị trên slide**:
  - Thực trạng: Bệnh lý tim mạch và rối loạn nhịp tim (Arrhythmia) là nguyên nhân gây đột tử hàng đầu thế giới; cần phát hiện sớm các nhịp nguy hiểm như Ngoại tâm thu thất (PVC) và Rung nhĩ (AFib).
  - Rào cản 1 (Vấn đề "Hộp đen" - Black-box): Các mô hình Deep Learning truyền thống chỉ đưa ra nhãn cảnh báo mà không giải thích được lý do bệnh học, khiến bác sĩ không dám tin cậy.
  - Rào cản 2 (Thiếu chuỗi tích hợp y sinh hoàn chỉnh): Đa số nghiên cứu dừng lại ở mức file Notebook rời rạc; thiếu chuỗi xử lý tín hiệu số y sinh (DSP), streaming thời gian thực độ trễ thấp và thiếu cơ chế Human-in-the-loop lưu vết pháp lý.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Sơ đồ đối sánh trực quan 2 cột: Cột trái "Mô hình Black-box $\rightarrow$ Bác sĩ hoài nghi $\rightarrow$ Không đưa vào ứng dụng" vs Cột phải "NEURO-ECG: Explainable AI + Human-in-the-loop $\rightarrow$ Đồng thuận y khoa & Ứng dụng thực tế".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Thưa các Thầy, AI đã đạt độ chính xác rất cao nhưng vẫn chưa thể vào bệnh viện vì hai rào cản lớn: tính 'hộp đen' và sự thiếu hụt một hệ thống tích hợp chuẩn y tế. Dự án của chúng em sinh ra để giải quyết triệt để hai bài toán này..."*

#### SLIDE 3: 1.2. MOTIVATION AND OBJECTIVE (Mục Tiêu & Giải Pháp Sản Phẩm)
- 🏷️ **Khung Template SIC**: *Template Unit 1.2: Motivation and Objective*
- 🎯 **Mục tiêu đánh giá**: Khái quát 5 mục tiêu cốt lõi của đề tài tạo nên một giải pháp y tế khép kín (Khẳng định tính sáng tạo và khả thi).
- **Nội dung hiển thị trên slide**:
  - Mục tiêu 1 (Lõi AI Đa mô hình): Benchmark 5 kiến trúc 1D (ResNet, CNN-LSTM, TCN, Transformer, Mamba); chọn ResNet-1D đạt Accuracy 98.57%, Macro-F1 91.70%, Latency 0.13ms.
  - Mục tiêu 2 (Explainable AI): Ứng dụng 1D Grad-CAM trích xuất bản đồ nhiệt minh bạch hóa căn cứ chẩn đoán trên phức bộ P-QRS-T.
  - Mục tiêu 3 (Y sinh & DSP): Xây dựng chuỗi lọc thông dải Butterworth, Notch 50Hz, Pan-Tompkins QRS đạt F1 = 97.14%, và module sàng lọc AFib.
  - Mục tiêu 4 (Tối ưu Edge AI): Lượng tử hóa ONNX INT8 nén mô hình xuống 697.3 KB (< 700 KB), ONNX FP32 chạy nhanh gấp 4 lần.
  - Mục tiêu 5 (Nền tảng Full-Stack & Human-in-the-loop): FastAPI WebSocket 360Hz 2 kênh, React 19 Plotly 60 FPS, RBAC 3 vai trò, Audit Trail và xuất báo cáo y tế PDF.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Sơ đồ 5 khối hình hộp tròn (5 Pillars of NEURO-ECG): `[DSP Pipeline] -> [ResNet-1D / ONNX] -> [1D Grad-CAM] -> [FastAPI WebSocket] -> [React 19 & Doctor Review]`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"NEURO-ECG được định hình không chỉ là một bài toán phân loại nhịp tim, mà là một hệ sinh thái y tế hoàn chỉnh từ xử lý tín hiệu thô đến thiết bị đeo và bàn làm việc của bác sĩ..."*

#### SLIDE 4: 1.3 & 1.4. ROLE ASSIGNMENTS & WBS MILESTONES (Phân Công & Tiến Độ)
- 🏷️ **Khung Template SIC**: *Template Unit 1.3 & 1.4: Role Assignments & WBS Milestones*
- 🎯 **Mục tiêu đánh giá**: Ăn trọn 15% điểm Kỹ năng làm việc nhóm & tiến độ WBS theo đúng biểu mẫu Action Plan / WBS của Samsung SIC.
- **Nội dung hiển thị trên slide**:
  - Phân công vai trò (Role by Member):
    - Nguyễn Đào Nam Hải (Trưởng nhóm): Kiến trúc mô hình AI (Benchmark 5 model, Grad-CAM, ONNX), Kiến trúc Backend FastAPI, WebSocket streaming 360Hz, Giao diện React 19.
    - Phan Thị Hải Yến (Thành viên): Kỹ thuật dữ liệu (Kaggle, PhysioNet WFDB, SMOTE, Validation Split), Chuỗi DSP (Pan-Tompkins QRS, Lọc dải thông), Thẩm định tiêu chuẩn y tế & Báo cáo QA.
  - Kế hoạch hành động & Tiến độ WBS (6 Checkpoints hoàn thành 100%):
    - W1-W2 (CP1-CP2): Dữ liệu, SMOTE, 5 Models, Grad-CAM, WebSocket core.
    - W3-W4 (CP3-CP4): DSP Pan-Tompkins, Báo động IEC 60601-1-8, Xuất PDF/CSV.
    - W5-W6 (CP5-CP6): Database RBAC, Human-in-the-loop, ONNX INT8, Test suite 42/42.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Bảng phân vai 2 thành viên kèm ảnh chân dung nhóm nhỏ và Biểu đồ tiến độ Gantt Chart / WBS 6 tuần với các mốc Checkpoint xanh hoàn thành.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Tuân thủ đúng quy trình quản lý dự án Capstone của Samsung SIC, nhóm em đã phân vai rõ ràng giữa mảng AI/Hệ thống và mảng Kỹ thuật Dữ liệu/DSP, bám sát từng mốc WBS trong suốt 6 tuần thực hiện..."*

---

### UNIT 2. PROJECT EXECUTION (Phương Pháp, Mô Hình AI & Kiến Trúc Hệ Thống)

#### SLIDE 5: 2.1. SYSTEM ARCHITECTURE & SERVICE MODEL (Kiến Trúc Dịch Vụ & Luồng Dữ Liệu)
- 🏷️ **Khung Template SIC**: *Template Unit 2.1: IoT Service Model & System Architecture*
- 🎯 **Mục tiêu đánh giá**: Trình bày kiến trúc phần mềm vi mô Client-Server xử lý luồng dữ liệu y tế thời gian thực (Ăn điểm Kỹ thuật hệ thống).
- **Nội dung hiển thị trên slide**:
  - Mô hình Client-Server hướng dịch vụ vi mô (Micro-modular Architecture):
    1. Tầng Ingestion: Tiếp nhận luồng tín hiệu 360Hz từ thiết bị/giả lập, đóng gói 36 gói tin/giây (10 mẫu/gói).
    2. Tầng Tiền xử lý DSP: Bộ lọc thông dải 0.5-45Hz, Notch 50Hz, thuật toán Pan-Tompkins tách đỉnh R.
    3. Tầng Suy luận AI (Singleton): Cắt cửa sổ 187 mẫu, đưa qua ResNet-1D / ONNX trả về nhãn, độ tin cậy và Grad-CAM.
    4. Tầng Điều phối Cảnh báo: Phân loại mức độ nguy cấp (Xanh - Vàng - Đỏ) và đẩy qua WebSocket.
    5. Tầng Ứng dụng & Bác sĩ: React 19 hiển thị 60 FPS, kích hoạt chuông báo và lưu vào hàng đợi thẩm định.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Sơ đồ kiến trúc phân tầng (5-layer Data Pipeline Architecture) vẽ bằng các khối phẳng chuyên nghiệp từ Ingestion $\rightarrow$ DSP $\rightarrow$ Inference $\rightarrow$ Alert $\rightarrow$ Web Client.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Hệ thống hoạt động theo đường ống xử lý liên hoàn, toàn bộ quá trình từ lúc mẫu tín hiệu phát ra đến khi kết quả suy luận hiển thị trên màn hình bác sĩ chỉ mất dưới 5 mili-giây..."*

#### SLIDE 6: 2.2. DATA PROCESSING & DSP PIPELINE (Xử Lý Dữ Liệu & Khắc Phục Data Leakage)
- 🏷️ **Khung Template SIC**: *Template Unit 2.2: Data Processing & DSP Pipeline*
- 🎯 **Mục tiêu đánh giá**: Làm nổi bật năng lực DSP và bài học học thuật về việc sửa lỗi rò rỉ dữ liệu khi kết hợp SMOTE với Validation Split.
- **Nội dung hiển thị trên slide**:
  - Chuỗi tiền xử lý DSP y sinh:
    - Bộ lọc thông dải Butterworth bậc 4 (0.5–45Hz): Triệt tiêu nhiễu thở (< 0.5Hz) và nhiễu cơ EMG (> 40Hz).
    - Bộ lọc chắn dải Notch 50Hz ($Q=30$): Triệt tiêu can nhiễu điện lưới xoay chiều.
    - Pan-Tompkins QRS Detection: Vi phân $\rightarrow$ Bình phương $\rightarrow$ Tích phân cửa sổ động $\rightarrow$ Ngưỡng thích ứng kép.
  - Xử lý mất cân bằng & Sửa lỗi Rò rỉ dữ liệu (Data Leakage):
    - Lớp N chiếm 82.8%, Lớp F chỉ 0.73% $\rightarrow$ Dùng SMOTE ($k=5$) cân bằng tập Train lên 326k mẫu.
    - Phát hiện & Sửa lỗi: Tách Stratified Validation (10%) TRƯỚC KHI SMOTE $\rightarrow$ Val (98.62%) ≈ Test (98.51%), lệch chỉ 0.11%, chứng minh mô hình không overfit.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/01_ecg_class_waveforms.png` (Hình thái 5 lớp sóng) và sơ đồ quy trình DSP 4 bước.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Bước DSP là bắt buộc để chuẩn hóa tín hiệu thực tế. Đặc biệt, việc phát hiện và sửa triệt để lỗi rò rỉ dữ liệu trước SMOTE là minh chứng cho tinh thần nghiên cứu nghiêm túc của nhóm..."*

#### SLIDE 7: 2.3. AI CORE: BENCHMARK 5 ARCHITECTURES & RESNET-1D (So Sánh 5 Kiến Trúc AI)
- 🏷️ **Khung Template SIC**: *Template Unit 2.3: Service / AI Implementation*
- 🎯 **Mục tiêu đánh giá**: Trình bày nghiên cứu thực nghiệm đối sánh 5 mô hình và chứng minh cơ sở khoa học chọn ResNet-1D.
- **Nội dung hiển thị trên slide**:
  - Nghiên cứu và tự cài đặt độc lập 5 kiến trúc Deep Learning 1D: ResNet1D, CNN1D-LSTM, TCN, Transformer1D, Mamba1D.
  - Kết quả đối sánh toàn diện:
    - ResNet-1D: Accuracy 98.43% - 98.57%, Macro-F1 91.70%, Latency 0.133 ms, Params 692k. (TOÀN DIỆN NHẤT ⭐)
    - CNN1D-LSTM: Accuracy 97.27%, Macro-F1 85.79%, Latency 0.122 ms, Params 242k.
    - TCN: Accuracy 96.17%, Macro-F1 82.81%, Latency 0.601 ms, Params 171k.
    - Transformer-1D: Accuracy 95.36%, Macro-F1 83.11%, Latency 0.592 ms, Params 69k.
    - Mamba-1D: Accuracy 94.45%, Macro-F1 79.28%, Latency 0.490 ms, Params 59k.
  - Kiến trúc ResNet-1D triển khai: Stem Conv1D $\rightarrow$ 3 khối Residual Blocks (kênh 32 $\rightarrow$ 64 $\rightarrow$ 128 $\rightarrow$ 256) với liên kết tắt $\rightarrow$ GAP $\rightarrow$ Linear 5.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/03_model_benchmark_comparison.png` (Biểu đồ so sánh 5 model) kèm bảng thông số tóm tắt.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Chúng em không chỉ chọn đại một mô hình mà đã benchmark công bằng cả 5 kiến trúc hiện đại nhất. ResNet-1D đạt F1 cao nhất 91.7% đồng thời có độ trễ suy luận chỉ 0.13ms, lý tưởng cho thời gian thực..."*

#### SLIDE 8: 2.4. EXPLAINABLE AI (1D GRAD-CAM) & AFIB SCREENING (Giải Thích Mô Hình & Sàng Lọc AFib)
- 🏷️ **Khung Template SIC**: *Template Unit 2.3: AI Implementation (XAI Innovation)*
- 🎯 **Mục tiêu đánh giá**: Làm nổi bật tính năng Explainable AI — điểm sáng tạo then chốt giải quyết rào cản 'hộp đen' y khoa (Ăn 25% điểm Sáng tạo).
- **Nội dung hiển thị trên slide**:
  - Thuật toán 1D Grad-CAM: Trích xuất trọng số chú ý $\alpha_k^c$ từ đạo hàm của điểm số phân loại đối với bản đồ đặc trưng tầng Conv cuối cùng $\rightarrow$ Chiếu bản đồ nhiệt Jet/Viridis trực tiếp lên sóng ECG.
  - Tương quan hoàn hảo với tri thức bệnh học lâm sàng:
    - Ngoại tâm thu thất (PVC - Lớp V): Vùng chú ý tập trung > 85% năng lượng vào phức bộ QRS giãn rộng (> 120ms) và sóng T đảo chiều.
    - Ngoại tâm thu nhĩ (PAC - Lớp S): Trọng số kích hoạt mạnh tại sóng P đến sớm bất thường.
    - Nhịp hợp nhất (Fusion - Lớp F): Bản đồ nhiệt phân bổ lưỡng cực tại cả sườn QRS và đoạn ST.
  - Module sàng lọc Rung nhĩ (AFib Screener): Phân tích rối loạn nhịp điệu kéo dài qua Shannon Entropy của dRR, hệ số biến thiên CV_RR và pNN50; kích hoạt khi vượt ngưỡng 0.62.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/06_gradcam_heatmaps_5_classes.png` (Bản đồ nhiệt 5 lớp sóng) và `figures/07_gradcam_vs_saliency_comparison.png`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Với 1D Grad-CAM, khi mô hình báo có nhịp ngoại tâm thu thất, bác sĩ nhìn thấy ngay vùng nhiệt đỏ rực tại phức bộ QRS giãn rộng. Điều này giúp bác sĩ hoàn toàn tin tưởng vào quyết định của AI..."*

#### SLIDE 9: 2.5. EDGE AI OPTIMIZATION (Lượng Tử Hóa ONNX INT8 & Triển Khai Nhúng)
- 🏷️ **Khung Template SIC**: *Template Unit 2.4: System Design & Edge Deployment*
- 🎯 **Mục tiêu đánh giá**: Chứng minh năng lực tối ưu hóa mô hình AI sẵn sàng triển khai trên thiết bị đeo IoT / Wearable Holter di động.
- **Nội dung hiển thị trên slide**:
  - Lượng tử hóa mô hình sang định dạng ONNX INT8:
    - Nén dung lượng: Giảm từ 2,735.5 KB (PyTorch) xuống 697.3 KB (ONNX INT8) $\rightarrow$ Giảm 74.5% dung lượng, hoàn thành mục tiêu thiết kế < 700 KB.
    - Bảo toàn độ chính xác: Độ chính xác end-to-end chỉ rớt 0.67 điểm % (94.33% $\rightarrow$ 93.66%, hoàn toàn nằm trong ngưỡng an toàn 2.0%).
    - Tăng tốc suy luận: Phiên bản ONNX FP32 đạt độ trễ 0.2918 ms/nhịp (tăng tốc gần 4 lần so với PyTorch gốc 1.14ms).
  - Khả năng ứng dụng Edge: Dung lượng dưới 700 KB cho phép nạp trực tiếp vào bộ nhớ flash của các vi điều khiển Edge AI (như Raspberry Pi 4, Jetson Nano, hoặc vi xử lý ARM hỗ trợ NEON dot-product).
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/10_onnx_quantization_comparison.png` (So sánh dung lượng, độ trễ và độ chính xác ONNX).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Mục tiêu Edge AI của chúng em là đưa mô hình vào các thiết bị di động nhỏ gọn. Kết quả nén xuống 697 KB qua ONNX INT8 giúp thiết bị Holter có thể tự phân loại nhịp tim mà không cần kết nối mạng..."*

---

### UNIT 3. RESULTS & DEMONSTRATION (Kết Quả Thực Nghiệm, Tính Hoàn Chỉnh & Live Demo)

#### SLIDE 10: 3.1. EXPERIMENTAL RESULTS & PAN-TOMPKINS VALIDATION (Kết Quả Thực Nghiệm Định Lượng)
- 🏷️ **Khung Template SIC**: *Template Unit 3.1: Data Processing Results*
- 🎯 **Mục tiêu đánh giá**: Cung cấp bằng chứng thực nghiệm định lượng vững chắc trên dữ liệu chuẩn quốc tế (Chứng minh chất lượng kỹ thuật).
- **Nội dung hiển thị trên slide**:
  - Kiểm chứng phân loại nhịp trên 21,892 nhịp test Kaggle MIT-BIH: Accuracy đạt 98.57%, Macro-F1 đạt 91.70%.
    - Lớp N: Precision 99.21%, Recall 99.19%, F1 99.20%.
    - Lớp V (PVC - Nguy hiểm nhất): Precision 95.02%, Recall 96.20%, F1 95.61%.
    - Lớp S (PAC): Precision 86.59%, Recall 81.29%, F1 83.86%.
  - Kiểm chứng phát hiện đỉnh R (Pan-Tompkins) trên 8 bản ghi thô PhysioNet (20,546 nhịp): F1 trung bình đạt 97.14%.
    - Bản ghi ít nhiễu (100, 234, 213): F1 đạt 99.98%.
    - Bản ghi nhiễu cơ/biến dạng nặng (200, 208, 203): F1 đạt 96.67% – 99.56%.
  - Kiểm chứng End-to-End từ tín hiệu thô 360Hz: Accuracy đạt 94.11% – 96.62% so với nhãn chuyên gia bác sĩ.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/04_resnet1d_confusion_matrix.png` (Ma trận nhầm lẫn) kèm bảng tóm tắt kết quả F1 Pan-Tompkins 8 bản ghi.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Mô hình đạt độ nhạy trên 96% ở lớp ngoại tâm thu thất — nhóm nhịp nguy hiểm nhất. Thuật toán Pan-Tompkins tự cài đặt cũng đạt F1 97.14% trên hơn 20 nghìn nhịp tim thực..."*

#### SLIDE 11: 3.2. FULL-STACK SYSTEM IMPLEMENTATION (Hạ Tầng Backend & Giao Diện Real-Time)
- 🏷️ **Khung Template SIC**: *Template Unit 3.2 & 3.3: Network, Communication & Service Implementation*
- 🎯 **Mục tiêu đánh giá**: Chứng minh tính hoàn chỉnh vượt trội của sản phẩm phần mềm y tế (Khẳng định 30% điểm Tính hoàn chỉnh).
- **Nội dung hiển thị trên slide**:
  - Backend FastAPI & Streaming WebSocket 360Hz 2 kênh:
    - Truyền đồng thời kênh chẩn đoán chính (MLII) và kênh tham chiếu phụ (V1/V2), 36 gói tin/giây, độ trễ < 5ms.
    - Mẫu thiết kế Inference Singleton nạp mô hình 1 lần duy nhất, loại bỏ nghẽn tài nguyên RAM.
    - Bộ theo dõi huyết động học: Đo liên tục nhịp tim (BPM) và biến thiên nhịp tim HRV (RMSSD, SDNN) trên cửa sổ 30 giây.
  - Cơ sở dữ liệu SQLite/SQLAlchemy & Phân quyền RBAC 3 vai trò:
    - 5 thực thể chuẩn: `users`, `patients`, `ecg_records`, `anomaly_events`, `audit_trails`.
    - Xác thực an toàn qua JSON Web Token (JWT) lưu trong HttpOnly Secure Cookie (chống XSS).
    - Phân quyền chặt chẽ: Admin (quản trị, cấu hình), Doctor (chẩn đoán, duyệt/sửa nhãn, xuất PDF), Nurse (giám sát, không sửa nhãn).
- 🎨 **Hình vẽ / Biểu đồ chèn**: Sơ đồ tương tác giữa Backend FastAPI, WebSocket 2 kênh, SQLite ORM và React 19 Frontend.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Khác với các đồ án chỉ dừng lại ở mô hình AI, chúng em đã xây dựng một hệ thống phần mềm hoàn chỉnh có phân quyền 3 vai trò, bảo mật cookie HttpOnly và streaming 2 kênh song song..."*

#### SLIDE 12: 3.3. MEDICAL USABILITY: HUMAN-IN-THE-LOOP & CHUẨN IEC 60601-1-8
- 🏷️ **Khung Template SIC**: *Template Unit 3.4: Data Visualization & Clinical Features*
- 🎯 **Mục tiêu đánh giá**: Nêu bật tính tuân thủ pháp lý y tế và tiêu chuẩn an toàn thiết bị y tế quốc tế (Điểm sáng tạo y khoa rất lớn).
- **Nội dung hiển thị trên slide**:
  - Cơ chế Human-in-the-loop: "AI hỗ trợ — Bác sĩ quyết định":
    - Bác sĩ có thể Xác nhận nhãn AI hoặc Ghi đè (Override) nhãn mới kèm lý do lâm sàng tại endpoint `/api/anomalies/{id}/verify`.
    - Bảng `audit_trails` tự động ghi nhận dấu thời gian, ID bác sĩ, nhãn cũ/mới, lý do y khoa $\rightarrow$ Đảm bảo tính minh bạch pháp lý tuyệt đối.
  - Hệ thống cảnh báo 3 cấp độ chuẩn an toàn quốc tế IEC 60601-1-8:
    - 🟢 Xanh (Bình thường) $\rightarrow$ 🟡 Vàng (Chú ý: PAC, nhịp chậm) $\rightarrow$ 🔴 Đỏ (Nguy cấp: PVC đa ổ, Rung nhĩ).
    - Tích hợp chuông báo âm thanh, đèn chớp và tính năng "Tắt chuông tạm thời 2 phút" (Alarm Mute) tự bật lại theo chuẩn IEC 60601-1-8.
  - Chẩn đoán ngoại tuyến & Xuất báo cáo: Upload tệp CSV/DAT; tạo tệp PDF bệnh án và bảng tính CSV lưu trữ hồ sơ bệnh nhân.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Ảnh chụp màn hình popup duyệt nhãn của bác sĩ kèm bảng Audit Trail và nút "Tắt chuông 2 phút chuẩn IEC 60601-1-8".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Trong y tế, tính năng Audit Trail và việc tuân thủ chuẩn an toàn báo động IEC 60601-1-8 là bắt buộc. Hệ thống của chúng em được thiết kế chuẩn mực theo tư duy của một thiết bị y tế thực thụ..."*

#### SLIDE 13: 3.4. TESTING, QUALITY ASSURANCE & DEVOPS (Kiểm Thử Tự Động & Đóng Gói Triển Khai)
- 🏷️ **Khung Template SIC**: *Template Unit 3.5: Testing and Improvements*
- 🎯 **Mục tiêu đánh giá**: Chứng minh chất lượng mã nguồn đạt chuẩn sản xuất với 100% test tự động pass và luồng CI/CD.
- **Nội dung hiển thị trên slide**:
  - Bộ kiểm thử tự động Backend (Pytest):
    - Đạt 42/42 bài kiểm thử tự động (100% PASS), bao phủ từ Xác thực Auth JWT, REST API, WebSocket streaming, DSP, đến phân quyền RBAC và Human-in-the-loop.
  - Kiểm tra chất lượng mã nguồn (Linting):
    - Backend: Ruff check sạch hoàn toàn cú pháp và cảnh báo bảo mật.
    - Frontend: Oxlint check sạch toàn bộ mã nguồn React 19.
  - Container hóa & DevOps:
    - Đóng gói Docker Compose 2 dịch vụ độc lập: backend FastAPI (Uvicorn) và frontend React (Nginx reverse proxy).
    - Tích hợp quy trình CI/CD tự động hóa trên GitHub Actions cho mọi lần kiểm thử và build Docker.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Ảnh chụp màn hình terminal lệnh pytest 42/42 xanh lá cây kèm logo Docker Compose và GitHub Actions CI/CD pipeline.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Chất lượng mã nguồn được bảo đảm bằng 42 bài kiểm thử tự động và quy trình CI/CD hoàn thiện, sẵn sàng triển khai trên bất kỳ hạ tầng bệnh viện nào..."*

#### SLIDE 14: 3.5. LIVE DEMONSTRATION SESSION (Kịch Bản Trình Diễn Hệ Thống Trực Tiếp)
- 🏷️ **Khung Template SIC**: *Template Unit 3: Live Demo Session*
- 🎯 **Mục tiêu đánh giá**: Thực hiện Live Demo 5 pha dứt khoát trên màn hình trình duyệt (Chinh phục 30% điểm Hoàn chỉnh sản phẩm).
- **Nội dung hiển thị trên slide**:
  - Kịch bản trình diễn 5 pha liên hoàn trên hệ thống thực tế (`http://localhost:5173`):
    - Pha 1 (Streaming 360Hz): Phát Record 100 (Bình thường), đồ thị 2 kênh mượt 60 FPS. Chuyển sang Record 200 (Bệnh nhân có nhiều PVC), AI lập tức bắt nhịp và dán nhãn màu đỏ 'Ventricular Ectopic' với độ tin cậy > 95%.
    - Pha 2 (Báo động IEC 60601-1-8): Kích hoạt chuông cảnh báo âm thanh; bấm nút 'Tắt chuông 2 phút'.
    - Pha 3 (Explainable AI 1D Grad-CAM): Nhấp vào nhịp PVC, quan sát bản đồ nhiệt Grad-CAM đỏ rực tại phức bộ QRS giãn rộng.
    - Pha 4 (Human-in-the-loop & Xuất PDF): Đăng nhập tài khoản Bác sĩ, duyệt/sửa nhãn, kiểm tra Audit Trail và bấm Xuất Báo cáo Bệnh án PDF.
    - Pha 5 (Chẩn đoán Offline & Edge AI): Upload file CSV phân tích trong vài giây; kiểm tra mô hình ONNX INT8 697.3 KB.
  - Kế hoạch dự phòng: Đã đóng gói sẵn Docker Compose và video 4K backup nếu gặp sự cố kết nối.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Hình mockup màn hình Dashboard lớn kèm thông điệp: "Kính mời Hội đồng cùng theo dõi thao tác trực tiếp trên màn hình".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Sau đây nhóm em xin phép được trình diễn trực tiếp hệ thống qua 5 pha kịch bản liên hoàn trên trình duyệt web..."*

---

### UNIT 4. PROJECTED IMPACT & LIMITATIONS (Tác Động Dự Án & Đánh Giá Giới Hạn Trung Thực)

#### SLIDE 15: 4.1. ACCOMPLISHMENTS AND PROJECTED IMPACT (Thành Tựu & Tác Động Thực Tiễn)
- 🏷️ **Khung Template SIC**: *Template Unit 4.1: Accomplishments and Benefits*
- 🎯 **Mục tiêu đánh giá**: Tổng kết giá trị thực tế của đề tài đối với nền y tế và công nghệ thiết bị đeo (Khẳng định tính thực tiễn 25%).
- **Nội dung hiển thị trên slide**:
  - Những thành tựu cốt lõi đã đạt được 100%:
    - Xây dựng thành công chuỗi công nghệ khép kín từ DSP $\rightarrow$ AI $\rightarrow$ XAI $\rightarrow$ Edge ONNX $\rightarrow$ Full-Stack Web y tế.
    - Độ chính xác 98.57%, độ trễ 0.13ms, dung lượng nhúng 697 KB đáp ứng hoàn hảo tiêu chuẩn thời gian thực.
  - Tác động thực tiễn & Lợi ích xã hội:
    - Đối với Bệnh viện / Phòng Cấp cứu: Giảm tải áp lực cho bác sĩ trực, phát hiện tức thì các nhịp nguy hiểm đe dọa tính mạng, minh bạch hóa nguyên nhân qua bản đồ nhiệt XAI.
    - Đối với Chăm sóc sức khỏe từ xa (Telehealth): Mở đường cho các thiết bị Holter đeo người thông minh giá thành thấp tự phân loại nhịp tim tại chỗ mà không cần internet.
    - Giá trị học thuật: Tạo lập bộ khung benchmark 5 kiến trúc và phương pháp 1D Grad-CAM chuẩn mực cho dữ liệu chuỗi thời gian y sinh.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Sơ đồ tác động 3 trụ cột: `[Phòng Cấp cứu Bệnh viện] - [Thiết bị Đeo Holter Di động] - [Nghiên cứu Học thuật Y sinh]`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Dự án mang lại tác động kép: vừa giúp giảm tải cho bác sĩ tại phòng hồi sức cấp cứu, vừa mở ra tiềm năng tích hợp vào các thiết bị đeo Holter thông minh theo dõi bệnh nhân từ xa..."*

#### SLIDE 16: 4.2. TECHNICAL LIMITATIONS AND FUTURE IMPROVEMENTS (Hạn Chế & Đánh Giá Trung Thực)
- 🏷️ **Khung Template SIC**: *Template Unit 4.2: Future Improvements & Known Limitations*
- 🎯 **Mục tiêu đánh giá**: Thể hiện tư duy khoa học trung thực, chỉ rõ 4 hạn chế kỹ thuật và giải pháp (Điểm mấu chốt gây ấn tượng mạnh với Hội đồng).
- **Nội dung hiển thị trên slide**:
  - 1. Khả năng tổng quát hóa trên các lớp hiếm (S/F) khi gặp dữ liệu ngoại vi (Domain Shift):
    - Kiểm nghiệm trên INCART, SVDB, EDB: Lớp N và V duy trì độ chính xác cao (78%-94%), nhưng lớp S và F bị sụt giảm Recall (SVDB Recall_S = 0.4%, EDB = 3.6%).
    - Nguyên nhân: Do sự sai khác về vị trí đạo trình đo giữa các máy và số lượng mẫu gốc quá ít trong tập train (2.5% và 0.7%).
    - Đã thử nghiệm Fine-tune trên INCART nâng Accuracy lên 93.18%. Giải pháp căn cơ là cần huấn luyện đa nguồn (Multi-database).
  - 2. Ngưỡng quy tắc Rung nhĩ (AFib = 0.62): Chọn theo thực nghiệm trên MIT-BIH, cần tiếp tục kiểm định mù trên toàn bộ tập PhysioNet AFDB.
  - 3. Cảm biến phần cứng IoT: Hệ thống hiện chạy qua WebSocket simulator chuẩn 360Hz; chưa hàn nối trực tiếp module cảm biến AD8232/MAX30003 + ESP32.
  - 4. Thử nghiệm lâm sàng: Toàn bộ kết quả đo trên tập chuẩn quốc tế; chưa thử nghiệm mù đôi trực tiếp tại bệnh viện.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Chèn ảnh `figures/09_cross_database_generalization.png` (Biểu đồ kiểm nghiệm tổng quát hóa trên 3 tập ngoại vi).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Chúng em nhìn nhận trung thực rằng mô hình có hiện tượng sụt giảm độ nhạy ở lớp hiếm S và F khi gặp dữ liệu ngoài do khác biệt đạo trình đo. Nhóm đã thử nghiệm fine-tune thành công lên 93.18% và xác định giải pháp triệt để là train đa nguồn..."*

---

### UNIT 5. TEAM REVIEW, CONCLUSION & Q&A (Tự Đánh Giá Nhóm, Kết Luận & Bảo Vệ)

#### SLIDE 17: 5.1. TEAM REVIEW, LESSONS LEARNED & ROADMAP (Tự Đánh Giá Nhóm & Lộ Trình)
- 🏷️ **Khung Template SIC**: *Template Unit 5: Team Member Review and Comment*
- 🎯 **Mục tiêu đánh giá**: Đáp ứng đúng mục Team Review của Samsung SIC template, thể hiện sự trưởng thành và tinh thần đồng đội.
- **Nội dung hiển thị trên slide**:
  - Tự đánh giá thành viên (Member Review & Comment):
    - Nguyễn Đào Nam Hải: "Dự án giúp em làm chủ toàn diện từ mô hình Deep Learning 1D, kỹ thuật XAI Grad-CAM đến hạ tầng WebSocket độ trễ thấp và kiến trúc y tế chuẩn mực."
    - Phan Thị Hải Yến: "Quá trình tiền xử lý dữ liệu và phát hiện đỉnh R giúp em hiểu sâu sắc về tín hiệu số y sinh và bài học khắc phục rò rỉ dữ liệu trong Machine Learning."
  - Lộ trình phát triển tương lai (3 Giai đoạn):
    - Giai đoạn 1 (Hiện tại): Hoàn thiện 100% hệ thống phần mềm Full-Stack, AI, XAI và Edge ONNX.
    - Giai đoạn 2 (Tiếp theo): Hàn nối mạch phần cứng cảm biến AD8232/MAX30003 kết nối ESP32 gửi dữ liệu qua WiFi/MQTT và kiểm định ngưỡng AFDB.
    - Giai đoạn 3 (Ứng dụng): Thử nghiệm lâm sàng tại các khoa Tim mạch bệnh viện.
- 🎨 **Hình vẽ / Biểu đồ chèn**: Bảng tự nhận xét 2 thành viên kèm sơ đồ Roadmap 3 giai đoạn hướng tới thương mại hóa thiết bị y tế.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Qua dự án Capstone SIC, cả hai thành viên trong nhóm đều đã trưởng thành vượt bậc về cả kỹ năng công nghệ thực chiến lẫn năng lực giải quyết vấn đề thực tế..."*

#### SLIDE 18: 5.2. CONCLUSION, ACKNOWLEDGMENTS & Q&A (Kết Luận, Lời Cảm Ơn & Phản Biện)
- 🏷️ **Khung Template SIC**: *Template Unit 6: Instructor Review & Q&A Session*
- 🎯 **Mục tiêu đánh giá**: Kết thúc bài thuyết trình trang trọng, lắng đọng và tự tin bước vào phiên hỏi đáp phản biện (Ăn trọn 10% điểm Phản biện).
- **Nội dung hiển thị trên slide**:
  - Kết luận: NEURO-ECG đã hoàn thành xuất sắc toàn bộ mục tiêu đề cương Capstone Project SIC 2026: Chính xác (98.57%), Nhanh (0.13ms), Minh bạch (1D Grad-CAM), Nhẹ cho Edge (ONNX 697KB), và An toàn pháp lý (Human-in-the-loop Audit Trail).
  - Lời cảm ơn chân thành:
    - Kính gửi lời cảm ơn sâu sắc đến Ban Giảng viên Chương trình Samsung Innovation Campus (SIC) 2026.
    - Chân thành cảm ơn các Thầy Cô giáo Viện CNTT&TT — Đại học Bách Khoa Hà Nội.
    - Cảm ơn Tập đoàn Điện tử Samsung (Samsung Electronics Vietnam) đã tài trợ và đồng hành.
  - Q & A: Nhóm kính mời Hội đồng Giảng viên đặt câu hỏi và đóng góp ý kiến!
- 🎨 **Hình vẽ / Biểu đồ chèn**: Dòng chữ lớn trang trọng: "XIN CHÂN THÀNH CẢM ƠN HỘI ĐỒNG GIẢNG VIÊN!" kèm khung chữ "PHIÊN HỎI ĐÁP PHẢN BIỆN — Q & A".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Trên đây là toàn bộ báo cáo đồ án tốt nghiệp Capstone Project của nhóm chúng em. Chúng em xin chân thành cảm ơn các Thầy và rất mong nhận được những câu hỏi phản biện từ Hội đồng!"*

---

## III. BỘ CÂU HỎI PHẢN BIỆN DỰ KIẾN TỪ HỘI ĐỒNG VÀ GỢI Ý TRẢ LỜI

### ❓ Câu hỏi 1 (Về tính hoàn chỉnh): Tại sao nhóm chọn kiến trúc 1D CNN mà không dùng 2D CNN chuyển ảnh phổ (Spectrogram)?
💡 **Gợi ý trả lời**: Mô hình 1D xử lý trực tiếp trên chuỗi tín hiệu thời gian nên có 3 ưu điểm vượt trội cho bài toán thời gian thực:
1. *Tiết kiệm tài nguyên*: Không mất chi phí tính toán biến đổi Fourier liên tục (STFT/CWT) sang ảnh phổ.
2. *Độ trễ suy luận siêu thấp*: Chỉ 0.13ms (so với hàng chục ms của 2D CNN), cho phép truyền phát mượt mà 36 gói/giây qua WebSocket.
3. *Dung lượng cực nhẹ*: Chỉ 692k tham số, dễ dàng lượng tử hóa xuống 697 KB để nhúng vào thiết bị đeo IoT.

### ❓ Câu hỏi 2 (Về hạn chế khoa học): Tại sao độ chính xác trên tập ngoài (INCART, SVDB, EDB) của lớp S và F lại bị giảm nhiều như vậy?
💡 **Gợi ý trả lời**: Thưa các Thầy, đây là hiện tượng Domain Shift kinh điển trong y sinh do 2 nguyên nhân cốt lõi:
1. Sự sai khác về vị trí đạo trình đo giữa các thiết bị ghi (ví dụ INCART dùng 12 chuyển đạo tiêu chuẩn, trong khi MIT-BIH dùng chuyển đạo sửa đổi MLII), khiến hình thái sóng P của lớp S bị biến dạng.
2. Số lượng mẫu lớp S và F trong tự nhiên quá ít (chỉ 2.5% và 0.7%), khiến mặt quyết định bị chèn ép. Nhóm đã thử nghiệm Fine-tune trên INCART nâng được độ chính xác lên 93.18%, và xác định giải pháp căn cơ là cần huấn luyện đa nguồn (Multi-database training) trong tương lai.

### ❓ Câu hỏi 3 (Về tính sáng tạo & y đức): Nếu AI đưa ra chẩn đoán sai thì hệ thống xử lý trách nhiệm y tế như thế nào?
💡 **Gợi ý trả lời**: Hệ thống của nhóm kiên định triết lý "AI chỉ là trợ lý sàng lọc, Bác sĩ mới là người quyết định cuối cùng". Khi AI phát hiện bất thường, nó chỉ gắn cờ cảnh báo kèm độ tin cậy và bản đồ nhiệt XAI. Bác sĩ chuyên khoa sẽ vào thẩm định, nếu AI sai bác sĩ có quyền bấm sửa nhãn. Mọi thao tác đều được hệ thống ghi tự động vào bảng Audit Trail với dấu thời gian chính xác, ID bác sĩ và lý do sửa nhãn để đảm bảo truy vết trách nhiệm pháp lý tuyệt đối.

### ❓ Câu hỏi 4 (Về kỹ thuật Edge AI): Tại sao bản lượng tử hóa ONNX INT8 không thấy nhanh hơn bản FP32 trên máy tính của nhóm?
💡 **Gợi ý trả lời**: Thưa các Thầy, đây là đặc tính kỹ thuật đã biết của cơ chế Dynamic Quantization trên CPU thông thường. Trên CPU máy dev không có tập lệnh tăng tốc phần cứng chuyên dụng (như Intel AVX-512 VNNI), ONNX Runtime phải tốn thêm phép tính lượng tử hóa các kích hoạt (activations) ngay lúc chạy. Tuy nhiên, bản INT8 đã hoàn thành xuất sắc mục tiêu nén dung lượng (giảm 74.5% còn 697 KB), và lợi ích tăng tốc của INT8 sẽ phát huy triệt để khi nạp lên các chip biên chuyên dụng như Jetson Nano (TensorRT INT8) hoặc ARM Cortex có hỗ trợ NEON dot-product.
