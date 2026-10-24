# DÀN Ý VÀ HƯỚNG DẪN THIẾT KẾ SLIDE THUYẾT TRÌNH BẢO VỆ ĐỒ ÁN TỐT NGHIỆP CAPSTONE PROJECT (AI TRACK)
## SAMSUNG INNOVATION CAMPUS (SIC) - HUST 2026

**ĐỀ TÀI**: **HỆ THỐNG GIÁM SÁT ECG THỜI GIAN THỰC TÍCH HỢP TRÍ TUỆ NHÂN TẠO GIẢI THÍCH ĐƯỢC (EXPLAINABLE AI) VÀ HỖ TRỢ CHẨN ĐOÁN RỐI LOẠN NHỊP TIM ĐA TẦNG (NEURO-ECG)**  
- **Nhóm thực hiện**: Nguyễn Đào Nam Hải (Trưởng nhóm) · Phan Thị Hải Yến  
- **Ngày bảo vệ chính thức**: 31/10/2026  
- **Tệp Word chi tiết**: [`docs/Dan_y_va_Huong_dan_Slide_Thuyet_trinh_SIC.docx`](Dan_y_va_Huong_dan_Slide_Thuyet_trinh_SIC.docx)  
- **Mã nguồn dự án**: [https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection](https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection)

---

## I. CHIẾN LƯỢC TỔNG QUAN VÀ PHÂN CÔNG THUYẾT TRÌNH

- **Thời lượng**: Tổng cộng 25 phút (15 phút trình bày slide + demo; 10 phút hỏi đáp phản biện).
- **Màu sắc & Phông chữ**:
  - Tone màu chủ đạo: **Xanh Navy (`#1E3A8A`)**, **Trắng/Xám nhạt (`#F8FAFC`)**, và **Đỏ y tế (`#DC2626`)** cho các điểm báo động nguy cấp.
  - Phông chữ: Không chân hiện đại (Inter, Roboto, Arial, Calibri); cỡ chữ tiêu đề 28–32pt, nội dung 18–22pt; không dùng animation chạy chữ rườm rà.
- **Phân công 2 sinh viên**:
  - **Sinh viên 1 (Nam Hải - Trưởng nhóm)**: Trình bày Slide 1 $\rightarrow$ 3 (Mở đầu, đặt vấn đề), Slide 6 $\rightarrow$ 12 (AI Benchmark, Explainable AI, ONNX, Backend, Frontend, RBAC) và trực tiếp điều khiển Live Demo 5 pha.
  - **Sinh viên 2 (Hải Yến - Thành viên)**: Trình bày Slide 4 $\rightarrow$ 5 (Dữ liệu, SMOTE, Sửa rò rỉ Validation, DSP Pan-Tompkins), Slide 13 $\rightarrow$ 15 (Đánh giá hoàn thành, Hạn chế kỹ thuật & Cross-database) và Slide 18 (Kết luận).

---

## II. DÀN Ý CHI TIẾT TỪNG SLIDE (SLIDE 1 ĐẾN SLIDE 18)

### SLIDE 1: TRANG TIÊU ĐỀ (TITLE SLIDE)
- 🎯 **Mục tiêu cần làm**: Giới thiệu đề tài trang trọng, tạo ấn tượng khoa học công nghệ y tế chuẩn mực.
- **Nội dung hiển thị**:
  - Tên đề tài: HỆ THỐNG GIÁM SÁT ECG THỜI GIAN THỰC TÍCH HỢP XAI VÀ HỖ TRỢ CHẨN ĐOÁN RỐI LOẠN NHỊP TIM ĐA TẦNG (NEURO-ECG)
  - Sinh viên: Nguyễn Đào Nam Hải (Trưởng nhóm) · Phan Thị Hải Yến
  - Đơn vị: Samsung Innovation Campus (SIC) 2026 — Đại học Bách Khoa Hà Nội
  - Kho lưu trữ GitHub: `https://github.com/NamHaiIT2HUST/ECG-Arrhythmia-Detection`
- 🎨 **Hình vẽ / Chèn ảnh**: Đặt Logo Bách Khoa và Logo Samsung 2 góc trên; hình nền phẳng tối giản có đường sóng điện tim mờ chạy ngang dưới chân trang.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Kính thưa các Thầy trong Hội đồng Giảng viên SIC và HUST, hôm nay nhóm chúng em xin phép trình bày đồ án tốt nghiệp Capstone Project: Hệ thống giám sát ECG thời gian thực tích hợp Explainable AI..."*

---

### SLIDE 2: BỐI CẢNH LÂM SÀNG & RÀO CẢN ĐƯA AI VÀO Y TẾ
- 🎯 **Mục tiêu cần làm**: Thuyết phục Hội đồng về tính cấp thiết thực tế và 2 rào cản lớn của AI trong y khoa.
- **Nội dung hiển thị**:
  - Thực trạng: Rối loạn nhịp tim (Arrhythmia) như Ngoại tâm thu thất (PVC) và Rung nhĩ (AFib) là nguyên nhân hàng đầu gây đột tử tim mạch và đột quỵ.
  - Rào cản 1 (Hộp đen): Bác sĩ không thể tin tưởng một mô hình AI chỉ báo nhãn mà không giải thích được căn cứ bệnh học.
  - Rào cản 2 (Thiếu chuỗi tích hợp y sinh): Đa số nghiên cứu dừng lại ở file Colab/Notebook rời rạc, thiếu DSP lọc nhiễu, thiếu WebSocket streaming 360Hz độ trễ thấp, và thiếu cơ chế Human-in-the-loop lưu vết kiểm toán pháp lý y tế.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ đối sánh 2 cột: Bên trái là "AI Hộp đen thông thường $\rightarrow$ Bác sĩ hoài nghi $\rightarrow$ Không dùng được" đối xứng với bên phải "Explainable AI + Human-in-the-loop $\rightarrow$ Bác sĩ đồng thuận & Ra quyết định".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Nhiều mô hình đạt trên 98% nhưng bác sĩ lâm sàng không dám dùng vì không ai chịu trách nhiệm khi AI sai. Mục tiêu của chúng em là phá vỡ chiếc hộp đen này bằng Explainable AI..."*

---

### SLIDE 3: MỤC TIÊU ĐỀ TÀI & KIẾN TRÚC SẢN PHẨM NEURO-ECG
- 🎯 **Mục tiêu cần làm**: Tóm lược toàn bộ giải pháp sản phẩm trong một góc nhìn hệ thống tổng thể.
- **Nội dung hiển thị**:
  - 5 trụ cột cốt lõi của NEURO-ECG:
    1. *AI Core*: Benchmark 5 kiến trúc, chọn ResNet-1D (Accuracy 98.57%, Macro-F1 91.70%, Latency 0.13ms).
    2. *Explainable AI*: 1D Grad-CAM trích xuất bản đồ nhiệt phân bổ trọng số chú ý tại sóng P, QRS, T.
    3. *Y sinh & DSP*: Bộ lọc Butterworth + Notch 50Hz, Pan-Tompkins QRS F1=97.14%, Sàng lọc AFib.
    4. *Edge AI*: Lượng tử hóa ONNX INT8 nén còn 697.3 KB (< 700 KB), ONNX FP32 chạy nhanh gấp 4 lần.
    5. *Full-Stack Y tế*: Streaming 360Hz 2 kênh, SQLite/RBAC 3 vai trò, Human-in-the-loop Audit Trail, xuất PDF/CSV.
- 🎨 **Hình vẽ / Chèn ảnh**: Vẽ 5 khối bo tròn kết nối nhau theo chuỗi mắt xích khép kín: `[DSP 360Hz] -> [ResNet-1D / ONNX] -> [1D Grad-CAM] -> [FastAPI WebSocket] -> [React 19 & Doctor Review]`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"NEURO-ECG không chỉ là một thuật toán học máy, mà là một hệ thống y tế toàn diện khép kín từ cảm biến, xử lý tín hiệu số, trí tuệ nhân tạo đến giao diện phòng hồi sức cấp cứu..."*

---

### SLIDE 4: DỮ LIỆU NGHIÊN CỨU & KHẮC PHỤC LỖI RÒ RỈ DỮ LIỆU (DATA LEAKAGE)
- 🎯 **Mục tiêu cần làm**: Làm rõ nguồn dữ liệu và bài học học thuật sâu sắc về Data Leakage (điểm cộng học thuật rất lớn).
- **Nội dung hiển thị**:
  - 2 nguồn dữ liệu: Kaggle MIT-BIH (109k nhịp, 125Hz) để huấn luyện & benchmark; Raw PhysioNet MIT-BIH (48 bản ghi, 360Hz 2 kênh) để chạy streaming và kiểm định end-to-end.
  - Mất cân bằng dữ liệu cực đoan: Lớp N chiếm 82.8%, Lớp F chỉ 0.73% $\rightarrow$ Dùng SMOTE ($k=5$) cân bằng tập Train lên 326k mẫu.
  - Bài học kỹ thuật về Data Leakage: Tách Validation sau SMOTE khiến Val Accuracy đạt 99.78% (ảo). Nhóm đã sửa triệt để: tách Stratified Validation (10%) TRƯỚC KHI chạy SMOTE $\rightarrow$ Val (98.62%) ≈ Test (98.51%), lệch 0.11%, chứng minh mô hình không overfit.
- 🎨 **Hình vẽ / Chèn ảnh**: Chèn ảnh `figures/01_ecg_class_waveforms.png` (Hình thái 5 lớp sóng AAMI) hoặc `figures/02_class_distribution_imbalance.png` (Biểu đồ mất cân bằng dữ liệu gốc vs sau SMOTE).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Phát hiện quan trọng của nhóm trong quá trình nghiên cứu là khắc phục lỗi rò rỉ dữ liệu khi kết hợp SMOTE với Validation split. Khi sửa đúng, Val và Test lệch nhau chỉ 0.11%, khẳng định tính tổng quát hóa thực chất..."*

---

### SLIDE 5: CHUỖI TIỀN XỬ LÝ TÍN HIỆU SỐ Y SINH (DSP) & THUẬT TOÁN PAN-TOMPKINS
- 🎯 **Mục tiêu cần làm**: Chứng minh năng lực xử lý tín hiệu y sinh thực thụ trước khi đưa vào mô hình AI.
- **Nội dung hiển thị**:
  - Lọc thông dải Butterworth bậc 4 (0.5–45Hz): Triệt tiêu nhiễu thở (< 0.5Hz) và nhiễu cơ EMG (> 40Hz).
  - Lọc chắn dải Notch 50Hz ($Q=30$): Triệt tiêu can nhiễu điện lưới xoay chiều sinh hoạt.
  - Thuật toán Pan-Tompkins QRS Detection: Vi phân bậc 1 $\rightarrow$ Bình phương $\rightarrow$ Tích phân cửa sổ động 150ms $\rightarrow$ Ngưỡng biên độ kép thích nghi động.
  - Kết quả kiểm chứng: F1 trung bình đạt 97.14% trên 8 bản ghi tiêu biểu (20,546 nhịp tim thô). Record 100: 99.98%, Record 200: 99.56%, Record 207: 89.70%.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ Pipeline 4 bước: `[Tín hiệu thô 360Hz] -> [Bandpass 0.5-45Hz] -> [Notch 50Hz] -> [Pan-Tompkins QRS] -> [Cửa sổ 187 mẫu 125Hz]` kèm bảng nhỏ kết quả F1 Pan-Tompkins.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Nếu không có bước DSP này, tín hiệu thô đưa thẳng vào AI sẽ bị tụt tỷ lệ nhận diện xuống chỉ còn 0.2%. Thuật toán Pan-Tompkins nhóm tự xây dựng đạt độ chính xác F1 97.14%..."*

---

### SLIDE 6: BENCHMARK 5 KIẾN TRÚC DEEP LEARNING 1D & MÔ HÌNH RESNET-1D
- 🎯 **Mục tiêu cần làm**: Trình bày nghiên cứu thực nghiệm đối sánh 5 kiến trúc và cơ sở khoa học chọn ResNet-1D.
- **Nội dung hiển thị**:
  - Benchmark 5 mô hình trên cùng tập dữ liệu: ResNet-1D, CNN1D-LSTM, TCN, Transformer-1D, Mamba-1D.
  - ResNet-1D chiến thắng toàn diện: Accuracy cao nhất (98.43% - 98.57%), Macro-F1 cao nhất (91.70%), Độ trễ suy luận thấp nhất (0.133 ms/nhịp, thông lượng 7,546 nhịp/giây).
  - Kiến trúc ResNet-1D: Stem Conv1D $\rightarrow$ 3 khối Residual Blocks (kênh 32 $\rightarrow$ 64 $\rightarrow$ 128 $\rightarrow$ 256) với kết nối tắt tránh tiêu biến đạo hàm $\rightarrow$ Global Average Pooling $\rightarrow$ Linear Classifier 5 lớp AAMI.
  - Chỉ số từng lớp: Lớp N (F1: 99.20%), Lớp V/PVC (Recall: 96.20%, F1: 95.61%), Lớp S (F1: 83.86%).
- 🎨 **Hình vẽ / Chèn ảnh**: Chèn ảnh `figures/03_model_benchmark_comparison.png` (So sánh 5 model) hoặc `figures/04_resnet1d_confusion_matrix.png` (Ma trận nhầm lẫn ResNet-1D).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Thay vì dùng một kiến trúc có sẵn, nhóm đã tự cài đặt và benchmark cả 5 kiến trúc hiện đại nhất hiện nay. ResNet-1D là lựa chọn hoàn hảo nhất cho hệ thống thời gian thực nhờ độ trễ chỉ 0.13ms..."*

---

### SLIDE 7: EXPLAINABLE AI: THUẬT TOÁN 1D GRAD-CAM
- 🎯 **Mục tiêu cần làm**: Làm nổi bật giá trị cốt lõi của tính năng giải thích được, tạo niềm tin cho giới y khoa.
- **Nội dung hiển thị**:
  - Công thức 1D Grad-CAM: Trích xuất trọng số chú ý $\alpha_k^c$ từ đạo hàm của điểm số phân loại đối với bản đồ đặc trưng tại tầng tích chập cuối cùng (Layer 3 Residual Block).
  - Trực quan hóa bản đồ nhiệt tương quan hoàn hảo với bệnh học tim mạch:
    - Ngoại tâm thu thất (PVC - Lớp V): Vùng chú ý tập trung > 85% năng lượng vào phức bộ QRS giãn rộng (> 120ms) và sóng T đảo chiều.
    - Ngoại tâm thu nhĩ (PAC - Lớp S): Trọng số kích hoạt mạnh tại sóng P đến sớm bất thường.
    - Nhịp hợp nhất (Fusion - Lớp F): Bản đồ nhiệt phân bổ lưỡng cực tại cả sườn QRS và đoạn ST.
- 🎨 **Hình vẽ / Chèn ảnh**: Chèn ảnh `figures/06_gradcam_heatmaps_5_classes.png` (Bản đồ nhiệt 5 dạng sóng) và `figures/07_gradcam_vs_saliency_comparison.png` (So sánh Grad-CAM nét hơn Vanilla Saliency).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Bác sĩ tim mạch luôn nhìn vào độ giãn rộng của phức bộ QRS để chẩn đoán ngoại tâm thu thất. Thật tuyệt vời là bản đồ nhiệt 1D Grad-CAM của nhóm cũng sáng rực đúng ở phức bộ QRS, chứng minh AI đã học đúng căn cứ y khoa..."*

---

### SLIDE 8: TỐI ƯU HÓA NHÚNG EDGE AI (ONNX INT8) & MODULE SÀNG LỌC RUNG NHĨ (AFIB)
- 🎯 **Mục tiêu cần làm**: Chứng minh tính khả thi đưa AI lên thiết bị nhúng di động và module phát hiện Rung nhĩ.
- **Nội dung hiển thị**:
  - Lượng tử hóa ONNX INT8:
    - Dung lượng nén: Giảm từ 2,735 KB xuống 697.3 KB (giảm 74.5%, đạt chuẩn đề cương < 700 KB).
    - Độ chính xác: Chỉ giảm 0.67 điểm % (94.33% $\rightarrow$ 93.66%, nằm trong ngưỡng an toàn 2%).
    - Tốc độ: ONNX FP32 đạt 0.29 ms/nhịp (tăng tốc gần 4 lần so với PyTorch gốc).
  - Module sàng lọc Rung nhĩ (AFib Screener): Phân tích rối loạn nhịp điệu kéo dài qua Shannon Entropy của sai phân dRR, hệ số biến thiên CV_RR và pNN50; kích hoạt cảnh báo khi vượt ngưỡng 0.62.
- 🎨 **Hình vẽ / Chèn ảnh**: Chèn ảnh `figures/10_onnx_quantization_comparison.png` (Biểu đồ so sánh dung lượng, độ trễ và độ chính xác ONNX).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Với kích thước chỉ 697 KB, mô hình hoàn toàn sẵn sàng để nhúng vào bộ nhớ vi điều khiển của các thiết bị đeo Holter thông minh mà không cần phụ thuộc vào server đám mây..."*

---

### SLIDE 9: KIẾN TRÚC HỆ THỐNG TỔNG THỂ & LUỒNG DỮ LIỆU THỜI GIAN THỰC
- 🎯 **Mục tiêu cần làm**: Trình bày kiến trúc phần mềm chuẩn kỹ sư, phân tầng xử lý mượt mà.
- **Nội dung hiển thị**:
  - Mô hình Client-Server hướng dịch vụ vi mô (Micro-modular Architecture):
    - Ingestion (360Hz): Đóng gói 36 gói tin/giây (10 mẫu/gói) truyền qua giao thức WebSocket hai chiều.
    - DSP Pipeline: Lọc thông dải 0.5-45Hz, Notch 50Hz, Pan-Tompkins R-peak detector.
    - Inference Singleton: Nạp mô hình PyTorch/ONNX duy nhất một lần vào RAM, độ trễ suy luận < 1ms.
    - Alert Dispatcher: Phân tầng báo động Xanh (Bình thường) $\rightarrow$ Vàng (Chú ý) $\rightarrow$ Đỏ (Nguy cấp).
    - Frontend React 19: Kết xuất dạng sóng 60 FPS, kích hoạt chuông cảnh báo và đưa vào hàng đợi chuyên gia duyệt.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ khối luồng dữ liệu 5 tầng từ Thiết bị đo/Giả lập $\rightarrow$ FastAPI Backend $\rightarrow$ React 19 Frontend $\rightarrow$ SQLite Database.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Hệ thống được thiết kế theo thời gian thực chuẩn y tế, toàn bộ thời gian từ lúc mẫu tín hiệu phát ra đến khi AI phân loại và hiển thị lên màn hình bác sĩ chỉ mất dưới 5 mili-giây..."*

---

### SLIDE 10: HẠ TẦNG BACKEND FASTAPI & WEBSOCKET STREAMING 2 CHUYỂN ĐẠO
- 🎯 **Mục tiêu cần làm**: Nêu bật các kỹ thuật tối ưu backend hiệu năng cao và đồng bộ đa kênh.
- **Nội dung hiển thị**:
  - WebSocket Streaming 360Hz 2 kênh đồng thời: Truyền song song kênh chẩn đoán chính (MLII) và kênh tham chiếu phụ (V1/V2).
  - Mẫu thiết kế Inference Singleton: Khởi tạo mô hình một lần duy nhất lúc máy chủ khởi động, loại bỏ hoàn toàn chi phí nạp lại mô hình.
  - Đo lường huyết động học thời gian thực: Tính toán đồng bộ nhịp tim trung bình (BPM) và độ biến thiên nhịp tim HRV (RMSSD, SDNN) trên cửa sổ trượt 30 giây.
  - Khả năng chịu tải: Thử nghiệm ổn định 10 kết nối streaming đồng thời trên 1 node backend thông thường.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ luồng WebSocket Payload: JSON message chứa cấu trúc đa trường `[timestamp, lead_primary, lead_secondary, beat_window, prediction, confidence, gradcam_heatmap]`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Việc stream đồng thời cả 2 chuyển đạo MLII và V1 giúp bác sĩ có cái nhìn đa chiều về trục điện tim, tương tự như màn hình monitor chuyên dụng trong phòng mổ..."*

---

### SLIDE 11: BẢO MẬT RBAC, CƠ CHẾ HUMAN-IN-THE-LOOP & AUDIT TRAIL Y TẾ
- 🎯 **Mục tiêu cần làm**: Khẳng định tính nhân văn, an toàn pháp lý y tế và triết lý "AI hỗ trợ — Bác sĩ quyết định".
- **Nội dung hiển thị**:
  - Phân quyền 3 vai trò (RBAC):
    - Admin: Toàn quyền cấu hình hệ thống, hiệu chỉnh ngưỡng nhạy cảnh báo.
    - Doctor: Xem giám sát, chẩn đoán XAI chuyên sâu, duyệt hoặc sửa nhãn của AI, ký xuất báo cáo bệnh án.
    - Nurse: Giám sát bệnh nhân, tiếp nhận hồ sơ; không có quyền sửa đổi nhãn chẩn đoán của AI.
  - Bảo mật: Xác thực JWT lưu trong HttpOnly Secure Cookie (triệt tiêu nguy cơ tấn công XSS).
  - Human-in-the-Loop & Audit Trail: Endpoint `POST /api/anomalies/{id}/verify` cho phép bác sĩ duyệt hoặc ghi đè (Override) nhãn AI. Bảng `audit_trails` lưu vết bất biến: Dấu thời gian, ID bác sĩ, nhãn cũ/mới, lý do y khoa.
- 🎨 **Hình vẽ / Chèn ảnh**: Bảng phân quyền 3 cột (Admin, Doctor, Nurse) kèm biểu tượng ổ khóa bảo mật và sơ đồ mũi tên quy trình: "AI cảnh báo $\rightarrow$ Bác sĩ thẩm định/sửa nhãn $\rightarrow$ Tự động ghi vào Audit Trail".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Trong y tế, trách nhiệm pháp lý là tối thượng. Tính năng Audit Trail đảm bảo mọi can thiệp sửa nhãn của bác sĩ đều được lưu vết minh bạch, sẵn sàng phục vụ công tác thanh tra y khoa..."*

---

### SLIDE 12: GIAO DIỆN WEB FRONTEND REACT 19 & CHUẨN AN TOÀN BÁO ĐỘNG IEC 60601-1-8
- 🎯 **Mục tiêu cần làm**: Giới thiệu các tính năng giao diện chuẩn y khoa và trải nghiệm người dùng tối ưu.
- **Nội dung hiển thị**:
  - Dashboard Real-time: Đồ thị sóng 2 kênh mượt mà 60 FPS bằng Plotly.js, tự động co giãn biên độ riêng từng kênh (Auto-scaling Y-axis).
  - Hệ thống cảnh báo 3 cấp độ chuẩn IEC 60601-1-8: 🟢 Xanh (Bình thường) $\rightarrow$ 🟡 Vàng (Chú ý) $\rightarrow$ 🔴 Đỏ (Nguy cấp).
  - Tính năng Tắt chuông tạm thời 2 phút (Alarm Mute): Tự động bật lại chuông sau 2 phút nếu nguy cơ bệnh lý chưa giải quyết, đúng chuẩn an toàn thiết bị y tế quốc tế IEC 60601-1-8.
  - Chẩn đoán ngoại tuyến & Xuất báo cáo: Hỗ trợ upload tệp CSV/DAT; tạo tệp báo cáo PDF và bảng tính CSV đầy đủ thông tin hành chính và đồ thị sóng.
- 🎨 **Hình vẽ / Chèn ảnh**: Ảnh chụp màn hình thực tế giao diện Dashboard đang chạy đồ thị ECG 2 kênh (chụp từ web app `http://localhost:5173`).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Giao diện không dùng các màu sắc sặc sỡ mà tuân thủ chuẩn công thái học y tế. Tính năng tắt chuông 2 phút tự bật lại được cài đặt đúng theo tiêu chuẩn an toàn thiết bị y tế IEC 60601-1-8..."*

---

### SLIDE 13: NHỮNG KẾT QUẢ ĐÃ HOÀN THÀNH 100% THEO ĐỀ CƯƠNG
- 🎯 **Mục tiêu cần làm**: Tổng kết tự tin, rõ ràng các chỉ tiêu đã nghiệm thu vượt mức cam kết ban đầu.
- **Nội dung hiển thị**:
  - Hoàn thành trọn vẹn cả 6 Checkpoint (CP1 đến CP6) và 4 hạng mục mở rộng:
    1. Nhận diện rối loạn nhịp tim: Accuracy 98.57% (chỉ tiêu > 95%), Macro-F1 91.70% (chỉ tiêu > 85%), Latency 0.13ms.
    2. Explainable AI: 1D Grad-CAM trích xuất bản đồ nhiệt giải thích trực quan từng nhịp tim cả trên stream và offline.
    3. Tiền xử lý DSP: Bộ lọc dải thông và thuật toán Pan-Tompkins đạt F1 = 97.14% trên 20,546 nhịp tim thô.
    4. Edge AI: ONNX INT8 dung lượng 697.3 KB (chỉ tiêu < 700 KB). ONNX FP32 đạt độ trễ 0.29 ms.
    5. Phần mềm Full-Stack: WebSocket 360Hz 2 kênh, quản lý bệnh nhân, RBAC 3 vai trò, Human-in-the-loop, xuất báo cáo PDF.
    6. Chất lượng kiểm thử: 42/42 bài test pytest pass 100%, Lint sạch lỗi, Docker Compose và CI/CD GitHub Actions sẵn sàng.
- 🎨 **Hình vẽ / Chèn ảnh**: Bảng checklist đối chiếu tiến độ 6 Checkpoint màu xanh lá cây với các icon tích xanh ✅ cho toàn bộ các hạng mục.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Nhìn lại toàn bộ quá trình, nhóm đã hoàn thành đầy đủ 100% tất cả các cam kết trong đề cương, mọi con số đo lường đều có bằng chứng kiểm thử tự động..."*

---

### SLIDE 14: ĐÁNH GIÁ TRUNG THỰC: HẠN CHẾ KỸ THUẬT & NGUYÊN NHÂN KHOA HỌC
- 🎯 **Mục tiêu cần làm**: Thể hiện tư duy khoa học trung thực, chỉ rõ nguyên nhân và giải pháp (điểm gây ấn tượng mạnh nhất).
- **Nội dung hiển thị**:
  - 1. Khả năng tổng quát hóa lớp hiếm (S/F) khi gặp dữ liệu ngoài (Domain Shift):
    - Kiểm nghiệm trên INCART, SVDB, EDB: Lớp N và V duy trì độ chính xác cao (78%-94%), nhưng lớp S và F bị sụt giảm Recall (SVDB Recall_S = 0.4%, EDB = 3.6%).
    - Nguyên nhân: Do sự sai khác về vị trí đạo trình đo giữa các máy và số lượng mẫu gốc quá ít trong tập train (chỉ chiếm 2.5% và 0.7%).
    - Giải pháp: Nhóm đã thử nghiệm Fine-tune trên INCART nâng Accuracy lên 93.18%. Về lâu dài cần huấn luyện đa nguồn (Multi-database).
  - 2. Ngưỡng quy tắc Rung nhĩ (AFib = 0.62): Chọn theo thực nghiệm trên MIT-BIH, chưa qua kiểm định mù trên toàn bộ tập PhysioNet AFDB.
  - 3. Cảm biến phần cứng IoT: Hệ thống hiện chạy qua WebSocket simulator chuẩn 360Hz; chưa hàn nối trực tiếp module cảm biến AD8232/MAX30003 + ESP32.
  - 4. Thử nghiệm lâm sàng: Chưa có điều kiện thử nghiệm mù đôi trực tiếp tại bệnh viện.
- 🎨 **Hình vẽ / Chèn ảnh**: Chèn ảnh `figures/09_cross_database_generalization.png` (Biểu đồ kiểm nghiệm tổng quát hóa trên 3 tập ngoại vi).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Chúng em không giấu giếm khuyết điểm: khi thử nghiệm trên các tập dữ liệu bên ngoài, lớp hiếm S và F bị tụt độ nhạy do khác biệt vị trí đặt điện cực. Nhóm đã thử nghiệm fine-tune thành công lên 93.18% và xác định giải pháp triệt để là train đa nguồn..."*

---

### SLIDE 15: ĐỀ XUẤT ĐỊNH HƯỚNG & XIN Ý KIẾN BAN GIẢNG VIÊN
- 🎯 **Mục tiêu cần làm**: Mở rộng tầm nhìn phát triển và cầu thị xin ý kiến định hướng từ Hội đồng.
- **Nội dung hiển thị**:
  - Nhóm kính mong nhận được ý kiến đóng góp từ các Thầy:
    1. *Về giải thuật AI*: Định hướng áp dụng kỹ thuật Loss Re-weighting hoặc Contrastive Learning để nâng cao năng lực biểu diễn cho lớp hiếm S và F khi huấn luyện đa nguồn.
    2. *Về kiểm định Rung nhĩ*: Thiết lập giao thức tối ưu hóa ngưỡng cảnh báo trên tập dữ liệu chuyên biệt PhysioNet AFDB.
    3. *Về chuẩn hóa y tế*: Góp ý về quy trình Human-in-the-loop và cấu trúc báo cáo bệnh án để tiếp cận sát nhất với tiêu chuẩn phần mềm thiết bị y tế (SaMD).
  - Lộ trình tương lai: Tích hợp vi điều khiển ESP32 và module cảm biến ECG AD8232/MAX30003 truyền dữ liệu thời gian thực qua giao thức WiFi/MQTT.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ Roadmap 3 giai đoạn: `[Giai đoạn 1: Hoàn thiện AI & Web (Hiện tại)] -> [Giai đoạn 2: Tích hợp phần cứng IoT ESP32 & AFDB] -> [Giai đoạn 3: Thử nghiệm lâm sàng tại bệnh viện]`.
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Chúng em rất mong nhận được sự định hướng của các Thầy về mặt thuật toán và chuẩn y tế để nhóm có thể tiếp tục phát triển đề tài thành một sản phẩm thiết bị y tế hoàn chỉnh..."*

---

### SLIDE 16: KỊCH BẢN LIVE DEMO 5 PHA TRỰC TIẾP
- 🎯 **Mục tiêu cần làm**: Giới thiệu kịch bản rõ ràng trước khi chuyển màn hình sang chạy demo trực tiếp.
- **Nội dung hiển thị**:
  - Kịch bản trình diễn 5 pha liên hoàn:
    - *Pha 1 (Streaming 360Hz)*: Phát Record 100 (Bình thường), đồ thị 2 kênh mượt mà 60 FPS, nhịp tim ~75 BPM. Chuyển sang Record 200 (Bệnh nhân có nhiều PVC), AI lập tức bắt nhịp và dán nhãn màu đỏ 'Ventricular Ectopic' với độ tin cậy > 95%.
    - *Pha 2 (Báo động chuẩn IEC 60601-1-8)*: Kích hoạt chuông âm thanh và đèn chớp đỏ; bấm nút 'Tắt tiếng tạm thời 2 phút'.
    - *Pha 3 (Explainable AI 1D Grad-CAM)*: Nhấp vào nhịp PVC trên đồ thị, bản đồ nhiệt Grad-CAM hiển thị đỏ rực tại phức bộ QRS giãn rộng.
    - *Pha 4 (Human-in-the-loop & Xuất PDF)*: Đăng nhập tài khoản Bác sĩ, duyệt/sửa nhãn, kiểm tra Audit Trail và nhấn nút xuất báo cáo bệnh án PDF.
    - *Pha 5 (Chẩn đoán ngoại tuyến & Edge AI)*: Tải file CSV ngoài phân tích trong vài giây; kiểm tra mô hình ONNX INT8 697.3 KB.
- 🎨 **Hình vẽ / Chèn ảnh**: Sơ đồ Timeline 5 bước đánh số 1 $\rightarrow$ 5 với các biểu tượng trực quan (Sóng ECG, Chuông báo động, Não bộ XAI, Bác sĩ duyệt nhãn, Tệp báo cáo PDF).
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Sau đây nhóm em xin phép trình diễn trực tiếp 5 pha kịch bản trên máy chủ thực tế để Hội đồng kiểm chứng các tính năng của hệ thống..."*

---

### SLIDE 17: TRÌNH DIỄN HỆ THỐNG TRỰC TIẾP (LIVE DEMO SESSION)
- 🎯 **Mục tiêu cần làm**: Giữ slide này trên màn hình máy chiếu trong lúc chuyển sang trình duyệt web thao tác demo.
- **Nội dung hiển thị**:
  - **TRÌNH DIỄN HỆ THỐNG TRỰC TIẾP TRÊN TRÌNH DUYỆT (LIVE DEMO)**
  - Địa chỉ truy cập hệ thống: `http://localhost:5173`
  - Tần số phát luồng: 360 Hz (36 gói/giây) qua giao thức WebSocket hai chiều
  - Kế hoạch dự phòng: Đã đóng gói sẵn Docker Compose và video 4K backup.
- 🎨 **Hình vẽ / Chèn ảnh**: Hình mockup màn hình Dashboard lớn kèm thông điệp: "Kính mời Hội đồng cùng theo dõi thao tác trực tiếp trên màn hình".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *(Chuyển sang màn hình trình duyệt web và thực hiện dứt khoát 5 bước demo trong khoảng 3 phút)*.

---

### SLIDE 18: KẾT LUẬN, LỜI CẢM ƠN & Q&A
- 🎯 **Mục tiêu cần làm**: Tổng kết ngắn gọn, bày tỏ lòng biết ơn và mở đầu tự tin cho phiên hỏi đáp phản biện.
- **Nội dung hiển thị**:
  - **Kết luận**: NEURO-ECG đã hiện thực hóa thành công một hệ thống giám sát rối loạn nhịp tim toàn diện: Độ chính xác cao (98.57%), Độ trễ thấp (0.13ms), Minh bạch nhờ Explainable AI (1D Grad-CAM), Nhẹ cho Edge AI (ONNX 697KB), và An toàn pháp lý nhờ Human-in-the-loop.
  - **Lời cảm ơn**: Chân thành cảm ơn Ban Giảng viên Samsung Innovation Campus (SIC) 2026, các Thầy Cô giáo Viện CNTT&TT — Đại học Bách Khoa Hà Nội và Tập đoàn Điện tử Samsung đã tạo điều kiện và tận tình hướng dẫn nhóm.
  - **Q & A**: Nhóm kính mời các Thầy trong Hội đồng đặt câu hỏi và đóng góp ý kiến!
- 🎨 **Hình vẽ / Chèn ảnh**: Dòng chữ lớn trang trọng: "XIN CHÂN THÀNH CẢM ƠN HỘI ĐỒNG GIẢNG VIÊN!" kèm khung chữ "PHIÊN HỎI ĐÁP — Q & A".
- 🎙️ **Lời thoại gợi ý (Speaker Notes)**: *"Trên đây là toàn bộ báo cáo đồ án tốt nghiệp của nhóm chúng em. Chúng em xin chân thành cảm ơn các Thầy và rất mong nhận được những câu hỏi phản biện từ Hội đồng!"*

---

## III. BỘ CÂU HỎI PHẢN BIỆN DỰ KIẾN TỪ HỘI ĐỒNG VÀ GỢI Ý TRẢ LỜI

### ❓ Câu hỏi 1: Tại sao nhóm không dùng các mô hình 2D CNN chuyển ảnh spectrogram mà lại dùng mô hình 1D (ResNet-1D)?
💡 **Gợi ý trả lời**: Mô hình 1D xử lý trực tiếp trên chuỗi tín hiệu thời gian nên có 3 ưu điểm vượt trội cho bài toán thời gian thực:
1. *Tiết kiệm tài nguyên*: Không mất chi phí tính toán biến đổi Fourier liên tục (STFT/CWT) sang ảnh phổ.
2. *Độ trễ suy luận siêu thấp*: Chỉ 0.13ms (so với hàng chục ms của 2D CNN), cho phép truyền phát mượt mà 36 gói/giây qua WebSocket.
3. *Dung lượng cực nhẹ*: Chỉ 692k tham số, dễ dàng lượng tử hóa xuống 697 KB để nhúng vào thiết bị đeo IoT.

### ❓ Câu hỏi 2: Tại sao độ chính xác trên tập ngoài (INCART, SVDB, EDB) của lớp S và F lại bị giảm nhiều như vậy?
💡 **Gợi ý trả lời**: Thưa các Thầy, đây là hiện tượng Domain Shift kinh điển trong y sinh do 2 nguyên nhân cốt lõi:
1. Sự sai khác về vị trí đạo trình đo giữa các thiết bị ghi (ví dụ INCART dùng 12 chuyển đạo tiêu chuẩn, trong khi MIT-BIH dùng chuyển đạo sửa đổi MLII), khiến hình thái sóng P của lớp S bị biến dạng.
2. Số lượng mẫu lớp S và F trong tự nhiên quá ít (chỉ 2.5% và 0.7%), khiến mặt quyết định bị chèn ép. Nhóm đã thử nghiệm Fine-tune trên INCART nâng được độ chính xác lên 93.18%, và xác định giải pháp căn cơ là cần huấn luyện đa nguồn (Multi-database training) trong tương lai.

### ❓ Câu hỏi 3: Nếu AI đưa ra chẩn đoán sai thì hệ thống xử lý trách nhiệm như thế nào?
💡 **Gợi ý trả lời**: Hệ thống của nhóm kiên định triết lý "AI chỉ là trợ lý sàng lọc, Bác sĩ mới là người quyết định cuối cùng". Khi AI phát hiện bất thường, nó chỉ gắn cờ cảnh báo kèm độ tin cậy và bản đồ nhiệt XAI. Bác sĩ chuyên khoa sẽ vào thẩm định, nếu AI sai bác sĩ có quyền bấm sửa nhãn. Mọi thao tác đều được hệ thống ghi tự động vào bảng Audit Trail với dấu thời gian chính xác, ID bác sĩ và lý do sửa nhãn để đảm bảo truy vết trách nhiệm pháp lý tuyệt đối.

### ❓ Câu hỏi 4: Tại sao bản lượng tử hóa ONNX INT8 không thấy nhanh hơn bản FP32 trên máy tính của nhóm?
💡 **Gợi ý trả lời**: Thưa các Thầy, đây là đặc tính kỹ thuật đã biết của cơ chế Dynamic Quantization trên CPU thông thường. Trên CPU máy dev không có tập lệnh tăng tốc phần cứng chuyên dụng (như Intel AVX-512 VNNI), ONNX Runtime phải tốn thêm phép tính lượng tử hóa các kích hoạt (activations) ngay lúc chạy. Tuy nhiên, bản INT8 đã hoàn thành xuất sắc mục tiêu nén dung lượng (giảm 74.5% còn 697 KB), và lợi ích tăng tốc của INT8 sẽ phát huy triệt để khi nạp lên các chip biên chuyên dụng như Jetson Nano (TensorRT INT8) hoặc ARM Cortex có hỗ trợ NEON dot-product.
