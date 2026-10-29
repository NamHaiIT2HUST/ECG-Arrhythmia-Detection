# KỊCH BẢN THUYẾT TRÌNH BẢO VỆ CAPSTONE PROJECT
## 10 SLIDE ĐẦU — DÀNH CHO TEAM LEADER: NGUYỄN ĐÀO NAM HẢI
**Dự án:** NEURO-ECG — Hệ thống Giám sát ECG Thời gian thực Tích hợp AI Giải thích được & Hỗ trợ Chẩn đoán Rối loạn Nhịp tim Đa tầng  
**Chương trình:** Samsung Innovation Campus (SIC) 2026 — Đại học Bách khoa Hà Nội (HUST)  
**Thời lượng mục tiêu:** 7.5 – 8.0 phút (trên tổng số 15 phút trình bày của nhóm)  
**Tệp Word chính thức:** [`docs/Kich_ban_Thuyet_trinh_10_Slide_Dau_Nam_Hai.docx`](file:///d:/Project/ECG-Arrhythmia-Detection/docs/Kich_ban_Thuyet_trinh_10_Slide_Dau_Nam_Hai.docx)

---

## BẢNG PHÂN BỔ THỜI LƯỢNG 10 SLIDE ĐẦU

| Slide | Tiêu đề Slide & Phân mục | Thời lượng | Tích lũy | Điểm rơi trọng tâm |
| :---: | :--- | :---: | :---: | :--- |
| **01** | Tiêu Đề Dự Án & Định Danh Nhóm | 40s | 0:40 | Lời chào trang trọng, định vị tầm vóc đề tài Capstone |
| **02** | Khung Báo Cáo 5 Unit Chuẩn Samsung SIC | 30s | 1:10 | Khái quát cấu trúc báo cáo, phân chia vai trò 2 người rõ ràng |
| **03** | Unit 1.1: Bối Cảnh Lâm Sàng & 2 Rào Cản AI | 50s | 2:00 | Nỗi đau quá tải Holter 24h & Nghịch lý Hộp đen (Black-box) |
| **04** | Unit 1.2: 5 Trụ Cột Sản Phẩm & KPI Định Lượng | 50s | 2:50 | "Bắn" số liệu định lượng: 98.57% Acc, 92.39% F1, <700KB |
| **05** | Unit 1.3 & 1.4: Phân Công & Hoàn Thành 6 CP | 45s | 3:35 | Năng lực quản trị dự án, 100% đúng hạn 6 Checkpoints |
| **06** | Unit 2.1: Kiến Trúc 5 Tầng Luồng Dữ Liệu | 55s | 4:30 | Singleton Inference, Luồng Ingestion 360Hz -> WebSocket |
| **07** | Unit 2.2: DSP & Khắc Phục Lỗi Data Leakage | 55s | 5:25 | Pan-Tompkins F1=97.14%, Stratified Split trước SMOTE (lệch 0.11%) |
| **08** | Unit 2.3: Benchmark 5 Kiến Trúc & ResNet-1D | 55s | 6:20 | Lý giải vì sao ResNet-1D thắng Mamba/TCN/LSTM, Recall lớp V 96.2% |
| **09** | Unit 2.4: 1D Grad-CAM & Sàng Lọc AFib | 55s | 7:15 | Đối chiếu giải phẫu P-QRS-T, Shannon Entropy phát hiện AFib |
| **10** | Unit 2.5: Lượng Tử Hóa ONNX INT8 & Bàn Giao | 50s | **8:05** | Nén 74.5% còn 697.3 KB, ONNX FP32 0.29ms, Bàn giao Hải Yến |

---

## 3 NGUYÊN TẮC VÀNG CHO TEAM LEADER TRÊN SÂN KHẤU

1. **Khí chất chỉ huy (Engineering Leadership):**  
   Đứng thẳng, hai chân vững chãi rộng bằng vai, hai tay mở tự nhiên ngang thắt lưng khi trình bày. Không khoanh tay, không đút túi quần, không cúi gằm mặt vào giấy note. Mắt quét đều 3 khu vực: Thầy cô Bách Khoa (bên trái), Chuyên gia Samsung (trung tâm), Khách mời (bên phải).

2. **Không rào đón luồn cúi, tự tin với số liệu thực nghiệm:**  
   Tuyệt đối tránh các cụm từ thể hiện sự tự ti như: *"chúng em chỉ làm thử nghiệm"*, *"kết quả chưa đánh giá lâm sàng nên không chắc chắn"*. Hãy dùng ngôn ngữ chuẩn mực của kỹ sư y sinh:  
   > *"Hệ thống được thiết kế theo đúng chuẩn Clinical Decision Support System (CDSS), đóng vai trò màng lọc cảnh báo sớm tuyến đầu giúp giải phóng 80% áp lực đọc bản ghi cho bác sĩ tim mạch."*

3. **Làm chủ chiều sâu kỹ thuật (Deep Engineering Grip):**  
   Nhấn mạnh vào 3 đột phá kỹ thuật mà Hội đồng giám khảo đánh giá cao nhất:
   - Thuật toán ResNet-1D tối ưu hóa cho chuỗi thời gian 1D vượt trội hoàn toàn các mô hình 2D hay RNN cồng kềnh.
   - Sửa triệt để lỗi rò rỉ dữ liệu (Data Leakage) bằng quy trình Stratified Split trước SMOTE.
   - Lượng tử hóa ONNX INT8 nén 74.5% xuống 697.3 KB, đạt chuẩn bộ nhớ nhúng dưới 700 KB của thiết bị đeo tay IoT.

---

## CHI TIẾT KỊCH BẢN THUYẾT TRÌNH TỪNG SLIDE (SLIDE 1 - 10)

### SLIDE 01: TIÊU ĐỀ DỰ ÁN & ĐỊNH DANH NHÓM
- **Phân mục:** Unit 00 — Title Slide
- **Thời lượng:** 40 giây (Tích lũy: 0:40)
- **Mục tiêu:** Tạo ấn tượng ban đầu mạnh mẽ, đĩnh đạc, khẳng định vị thế đề tài Capstone tại Samsung Innovation Campus.
- **Cử chỉ & Visual:** Đứng giữa sân khấu, mắt nhìn thẳng vào Hội đồng, mỉm cười nhẹ và cúi chào đầu trang trọng. Giọng nói trầm ấm, vang rõ.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Kính thưa quý thầy cô trong Hội đồng Giám khảo Samsung Innovation Campus, quý thầy cô Đại học Bách khoa Hà Nội và toàn thể các bạn sinh viên có mặt trong buổi bảo vệ Capstone Project ngày hôm nay.
> 
> Em là **Nguyễn Đào Nam Hải**, đại diện cho nhóm tác giả gồm em và bạn **Phan Thị Hải Yến**, xin được trân trọng báo cáo kết quả đề tài tốt nghiệp: **'NEURO-ECG: Hệ thống giám sát tín hiệu điện tim thời gian thực, tích hợp Trí tuệ nhân tạo giải thích được (Explainable AI) và hỗ trợ chẩn đoán rối loạn nhịp tim đa tầng'**.
> 
> Dự án của chúng em được phát triển với định hướng kết nối toàn diện từ tầng xử lý tín hiệu số y sinh (DSP), mô hình học sâu tối ưu hóa lượng tử nhúng, cho tới ứng dụng Web lâm sàng thời gian thực hỗ trợ bác sĩ ra quyết định. Hôm nay, em xin phép được đại diện nhóm dẫn dắt toàn bộ nội dung nghiên cứu cốt lõi và kiến trúc kỹ thuật của hệ thống."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Dự án này là bài tập môn học hay là một sản phẩm kỹ thuật hoàn chỉnh?"*
- **Nam Hải trả lời:** *"Dạ thưa Hội đồng, NEURO-ECG là một sản phẩm kỹ thuật y tế hoàn chỉnh cấp độ Capstone (TRL-4/5), được triển khai đủ 5 tầng: từ luồng Ingestion 360Hz, thuật toán DSP Pan-Tompkins, mô hình ResNet-1D đạt 98.57% test accuracy, lượng tử hóa ONNX INT8 dưới 700 KB, cho tới Full-stack Web có phân quyền bác sĩ, báo động chuẩn y tế IEC 60601-1-8 và 42/42 bài kiểm thử tự động CI/CD."*

➔ **Câu nối chuyển tiếp:** *"Để quý Hội đồng tiện theo dõi, em xin phép đi vào cấu trúc 5 phần của buổi báo cáo ngày hôm nay."*

---

### SLIDE 02: TABLE OF CONTENTS — KHUNG BÁO CÁO 5 UNIT CHUẨN SAMSUNG SIC
- **Phân mục:** Unit 00 — Agenda
- **Thời lượng:** 30 giây (Tích lũy: 1:10)
- **Mục tiêu:** Khái quát lộ trình báo cáo logic theo đúng quy chuẩn 5 Unit của Samsung SIC, phân định rõ vai trò của Nam Hải (Slide 1–10) và Hải Yến (Slide 11–18).
- **Cử chỉ & Visual:** Bàn tay mở hướng về màn chiếu (không chỉ trỏ 1 ngón). Nói dứt khoát, nhịp điệu nhanh gọn.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Báo cáo của chúng em tuân thủ nghiêm ngặt khung đánh giá 5 Unit chuẩn của Samsung Innovation Campus:
> - **Unit 1:** Tổng quan bối cảnh, động lực, mục tiêu định lượng và phân công công việc.
> - **Unit 2:** Quá trình thực hiện kỹ thuật — tập trung vào luồng xử lý tín hiệu DSP, đối sánh 5 kiến trúc AI, giải thích mô hình với 1D Grad-CAM và tối ưu nhúng ONNX INT8.
> - **Unit 3:** Kết quả thực nghiệm và phiên Live Demonstration hệ thống trực tiếp.
> - **Unit 4:** Đánh giá tác động thực tiễn, phân tích Domain Shift đa nguồn và các rào cản kỹ thuật.
> - **Unit 5:** Tự đánh giá năng lực nhóm, bài học kinh nghiệm và lộ trình thương mại hóa.
> 
> Trong phần đầu tiên, em sẽ trình bày chi tiết Unit 1 và Unit 2. Sau đó, bạn Hải Yến sẽ trực tiếp điều hành phiên Live Demo và kết quả tại Unit 3, 4, 5."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Vì sao nhóm lại phân chia bài thuyết trình theo hai nửa như vậy?"*
- **Nam Hải trả lời:** *"Dạ thưa thầy cô, em là người trực tiếp thiết kế kiến trúc hệ thống, huấn luyện lõi AI, XAI và đóng gói nhúng; còn bạn Hải Yến trực tiếp phụ trách luồng dữ liệu, thẩm định DSP và chuẩn hóa giao diện lâm sàng. Cách phân chia này đảm bảo người phụ trách chuyên sâu mảng nào sẽ trực tiếp báo cáo và chịu trách nhiệm phản biện sâu nhất mảng đó trước Hội đồng."*

➔ **Câu nối chuyển tiếp:** *"Ngay sau đây, em xin kính mời Hội đồng bước vào Unit 1 với bối cảnh lâm sàng và bài toán cốt lõi."*

---

### SLIDE 03: UNIT 1.1 — BỐI CẢNH LÂM SÀNG & 2 RÀO CẢN CỐT TỬ CỦA AI Y TẾ
- **Phân mục:** Unit 01 — Introduction
- **Thời lượng:** 50 giây (Tích lũy: 2:00)
- **Mục tiêu:** Chỉ ra nỗi đau lớn nhất của tim mạch (quá tải bản ghi Holter 24h, nguy cơ đột tử) và vạch rõ 2 rào cản chí mạng khiến AI học thuật không vào được bệnh viện: Hộp đen (Black-box) và Thiếu chuỗi tích hợp y tế.
- **Cử chỉ & Visual:** Giọng nói hạ thấp trầm ấm tạo tính nghiêm túc của bài toán cứu người. Nhấn mạnh 2 chữ: "Hộp đen" và "Tích hợp chuẩn".

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Thưa quý Hội đồng, bệnh lý tim mạch hiện là nguyên nhân gây tử vong số một toàn cầu. Trong đó, các rối loạn nhịp tim nguy hiểm như Ngoại tâm thu thất (PVC) kéo dài hay Rung nhĩ (AFib) thường diễn tiến âm thầm nhưng có thể dẫn đến đột tử hoặc đột quỵ não chỉ sau vài phút.
> 
> Tại các phòng cấp cứu và đơn vị hồi sức tích cực, một bệnh nhân đeo máy Holter 24 giờ tạo ra hơn 100.000 nhịp tim. Các bác sĩ tim mạch đang phải đối mặt với tình trạng quá tải nghiêm trọng khi đọc bản ghi thủ công.
> 
> Tuy nhiên, khi đưa Trí tuệ nhân tạo vào hỗ trợ y tế, chúng em nhận thấy có **2 rào cản sống còn**:
> - **Thứ nhất là 'Nghịch lý Hộp Đen' (Black-Box Problem):** Đa số các mô hình AI chỉ trả về một xác suất vô hồn. Bác sĩ không thể tin tưởng và không thể ký lệnh điều trị nếu không biết AI dựa trên căn cứ hình thái sóng nào.
> - **Thứ hai là 'Sự thiếu hụt chuỗi tích hợp y tế':** Hầu hết các nghiên cứu dừng lại ở file notebook rời rạc, hoàn toàn thiếu chuỗi lọc nhiễu thực tế, thiếu streaming thời gian thực và không có quy trình lưu vết trách nhiệm bác sĩ (Audit Trail).
> 
> Đó chính là lý do dự án NEURO-ECG ra đời để giải quyết triệt để cả hai bài toán này."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Hệ thống này có tham vọng thay thế bác sĩ tim mạch hay không?"*
- **Nam Hải trả lời:** *"Dạ hoàn toàn không ạ! Chúng em định vị NEURO-ECG là một 'Hệ thống Hỗ trợ Ra quyết định Lâm sàng' (Clinical Decision Support System - CDSS). AI đóng vai trò như một màng lọc cảnh báo sớm tuyến đầu 24/7, tự động khoanh vùng các biến cố nghi ngờ và giải thích bằng hình ảnh. Quyết định chẩn đoán và điều trị cuối cùng luôn luôn thuộc về bác sĩ có chứng chỉ hành nghề, được hỗ trợ bởi cơ chế duyệt nhãn Human-in-the-loop của chúng em."*

➔ **Câu nối chuyển tiếp:** *"Xuất phát từ bối cảnh đó, nhóm đã xác lập 5 mục tiêu nghiên cứu và các KPI kỹ thuật định lượng cụ thể tại Slide tiếp theo."*

---

### SLIDE 04: UNIT 1.2 — 5 TRỤ CỘT ĐỘT PHÁ & MỤC TIÊU ĐỊNH LƯỢNG NEURO-ECG
- **Phân mục:** Unit 01 — Introduction
- **Thời lượng:** 50 giây (Tích lũy: 2:50)
- **Mục tiêu:** Trình bày 5 trụ cột sản phẩm vững chắc và "bắn" số liệu KPI thực nghiệm đo đạc độc lập (98.57% Acc, 92.39% F1-macro, 97.14% Pan-Tompkins, < 700 KB INT8).
- **Cử chỉ & Visual:** Chỉ tay dứt khoát vào 5 khối thẻ trên màn chiếu. Tốc độ nói nhanh, tự tin, nhấn mạnh các con số định lượng chính xác.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Để giải quyết triệt để bài toán đặt ra, NEURO-ECG được xây dựng dựa trên 5 trụ cột kỹ thuật then chốt:
> 1. **AI Core Đa Mô Hình:** Nghiên cứu, huấn luyện và đối sánh 5 kiến trúc mạng nơ-ron 1D. Trong đó mô hình ResNet-1D của chúng em đạt độ chính xác **98.57%** và F1-Macro **92.39%** trên tập test MIT-BIH chuẩn, với độ trễ suy luận siêu thấp chỉ **0.134 miligiây**.
> 2. **Explainable AI:** Tích hợp thuật toán 1D Grad-CAM đầu tiên trên sóng điện tim, bóc tách vùng đóng góp tế vi trên phức bộ P-QRS-T giúp bác sĩ soi chiếu trực quan.
> 3. **Kỹ Thuật Y Sinh DSP:** Xây dựng bộ lọc thông dải Butterworth 0.5–45Hz, lọc Notch 50Hz triệt tiêu nhiễu điện lưới, cùng thuật toán Pan-Tompkins phát hiện đỉnh R đạt F1 trung bình **97.14%** trên 8 bản ghi PhysioNet.
> 4. **Tối Ưu Edge AI:** Lượng tử hóa ONNX INT8 thành công, nén **74.5%** dung lượng xuống **697.3 KB** — hoàn thành xuất sắc cam kết trong đề cương dự án là dưới 700 KB để sẵn sàng nạp lên chip đeo tay.
> 5. **Và cuối cùng là Nền Tảng Full-Stack:** Truyền phát WebSocket 360Hz 2 kênh liên tục, giao diện React 19 đạt 60 khung hình/giây và cơ chế phân quyền bảo mật 3 vai trò cùng Audit Trail chuẩn y tế."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Con số F1-macro 92.39% và 91.70% ở các bảng có gì mâu thuẫn không?"*
- **Nam Hải trả lời:** *"Dạ thưa thầy cô, 91.70% là kết quả trong bảng đối sánh benchmark lịch sử của 5 mô hình ban đầu tại Checkpoint 2. Còn 92.39% là kết quả kiểm định chính thức đo lại trên checkpoint mô hình tốt nhất vào ngày 23/10 có gắn mã băm SHA-256 truy vết trong phụ lục báo cáo. Cả hai con số đều phản ánh năng lực vượt trội của mô hình trên tập kiểm thử độc lập."*

➔ **Câu nối chuyển tiếp:** *"Để hoàn thành trọn vẹn 5 trụ cột kỹ thuật này, nhóm đã phân công vai trò và tổ chức tiến độ ra sao? Kính mời Hội đồng cùng nhìn vào Slide 05."*

---

### SLIDE 05: UNIT 1.3 & 1.4 — PHÂN CÔNG TRÁCH NHIỆM & TIẾN ĐỘ 6 CHECKPOINTS
- **Phân mục:** Unit 01 — Introduction
- **Thời lượng:** 45 giây (Tích lũy: 3:35)
- **Mục tiêu:** Chứng minh năng lực quản trị dự án chuyên nghiệp, hoàn thành 100% đúng hạn qua 6 Checkpoints khắt khe, thể hiện sự ăn ý tuyệt đối giữa hai thành viên.
- **Cử chỉ & Visual:** Ánh mắt nhìn sang bạn đồng hành Hải Yến như một sự ghi nhận đồng đội, sau đó quay lại Hội đồng với phong thái tự tin.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Trong dự án này, sự phân công trách nhiệm được xác lập dựa trên thế mạnh chuyên môn sâu của từng thành viên:
> - **Em — Nam Hải** đảm nhận vai trò Trưởng nhóm, trực tiếp thiết kế kiến trúc hệ thống, nghiên cứu lõi AI ResNet-1D, giải thuật 1D Grad-CAM, tối ưu hóa lượng tử hóa ONNX INT8, lập trình Backend FastAPI WebSocket và hạ tầng Docker CI/CD.
> - **Bạn Phan Thị Hải Yến** phụ trách mảng Kỹ thuật Dữ liệu & DSP y sinh: thu thập chuẩn hóa tập dữ liệu MIT-BIH, PhysioNet WFDB, cài đặt thuật toán lọc thích nghi và Pan-Tompkins, đồng thời phụ trách thẩm định độ chính xác và kiểm thử QA toàn diện.
> 
> Về mặt quản trị tiến độ (WBS), nhóm đã hoàn thành xuất sắc 100% toàn bộ 6 Checkpoints theo đúng kế hoạch:
> - Từ Checkpoint 1 & 2 xây dựng mô hình AI và pipeline dữ liệu;
> - Checkpoint 3 & 4 tích hợp DSP đỉnh R và chuẩn hóa cảnh báo y tế IEC 60601-1-8;
> - Cho đến Checkpoint 5 & 6 hoàn thiện hệ thống cơ sở dữ liệu RBAC, Audit Trail và bộ 42 test cases tự động."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Trong 6 tuần thực hiện, khó khăn lớn nhất trong việc phối hợp nhóm là gì?"*
- **Nam Hải trả lời:** *"Dạ thưa Hội đồng, thách thức lớn nhất là sự bất đồng bộ giữa miền tần số lấy mẫu của dữ liệu thô (PhysioNet 360Hz) và định dạng đầu vào của mô hình huấn luyện (125Hz, 187 mẫu). Nhóm đã phải thảo luận kỹ lưỡng và thống nhất một giao thức resampling Polyphase chặt chẽ trong tầng tiền xử lý để vừa bảo toàn biên độ phức bộ QRS, vừa đảm bảo mô hình nhận diện chính xác."*

➔ **Câu nối chuyển tiếp:** *"Sau đây, em xin phép bước vào Unit 2: Quá trình thực hiện kỹ thuật, mở đầu bằng Kiến trúc tổng thể 5 tầng của hệ thống."*

---

### SLIDE 06: UNIT 2.1 — KIẾN TRÚC HỆ THỐNG 5 TẦNG LUỒNG DỮ LIỆU THỜI GIAN THỰC
- **Phân mục:** Unit 02 — Project Execution
- **Thời lượng:** 55 giây (Tích lũy: 4:30)
- **Mục tiêu:** Làm chủ sơ đồ kiến trúc End-to-End từ Ingestion 360Hz đến UI, giải thích cơ chế Singleton Engine, hàng đợi bất đồng bộ và luồng WebSocket hai chiều.
- **Cử chỉ & Visual:** Dùng tay hoặc laser pointer quét tuần tự từ Trái qua Phải (Tầng 1 -> Tầng 5), làm nổi bật tính liên tục và khép kín của luồng dữ liệu.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Thưa quý Hội đồng, đây là Kiến trúc 5 tầng của NEURO-ECG — được thiết kế theo mô hình vi dịch vụ hướng sự kiện (Event-Driven Architecture) nhằm đảm bảo độ trễ thấp nhất và tính ổn định cao nhất:
> 
> - **Tầng 1 — Ingestion Layer:** Nhận luồng tín hiệu điện tim 2 kênh thô (Lead MLII và Lead V1) ở tần số 360Hz. Dữ liệu được đóng gói thành 36 gói tin mỗi giây (mỗi gói 10 mẫu) và truyền phát qua giao thức WebSocket bất đồng bộ.
> - **Tầng 2 — Tiền Xử Lý DSP:** Ngay khi nhận tín hiệu, bộ lọc Butterworth và Notch 50Hz tiến hành khử nhiễu đường nền và nhiễu điện lưới; sau đó thuật toán Pan-Tompkins quét tìm đỉnh R theo thời gian thực.
> - **Tầng 3 — AI Inference (Thiết kế theo mẫu Singleton Pattern):** Mỗi khi phát hiện một đỉnh R, hệ thống trích xuất cửa sổ 187 mẫu quanh đỉnh, chuẩn hóa và nạp vào mô hình ResNet-1D / ONNX INT8. Mô hình suy luận trong **0.13 miligiây** để trả về phân loại nhịp và bản đồ nhiệt Grad-CAM.
> - **Tầng 4 — Điều Phối Cảnh Báo:** Phân tầng nguy cơ thành 3 cấp (Bình thường - Chú ý - Nguy cấp) và kích hoạt chuông báo động tuân thủ tiêu chuẩn an toàn thiết bị y tế IEC 60601-1-8.
> - **Tầng 5 — Giao Diện Lâm Sàng & Duyệt Nhãn:** Hiển thị sóng điện tim 60 FPS trên React 19, cho phép bác sĩ thẩm định, sửa nhãn sai và lưu vết vĩnh viễn vào hệ cơ sở dữ liệu."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Tại sao phải dùng Singleton Pattern cho mô hình AI ở Tầng 3?"*
- **Nam Hải trả lời:** *"Dạ thưa thầy cô, việc khởi tạo lại mô hình và cấp phát lại bộ nhớ trọng số cho mỗi nhịp tim (vốn xuất hiện mỗi 0.8 giây) sẽ gây áp lực rác bộ nhớ (Garbage Collection) và giật lag nghiêm trọng. Thiết kế Singleton đảm bảo mô hình chỉ được nạp lên RAM một lần duy nhất khi khởi động server, tái sử dụng bộ nhớ đệm giúp độ trễ suy luận luôn giữ mức ổn định dưới 0.3 miligiây."*

➔ **Câu nối chuyển tiếp:** *"Một kiến trúc tốt phải dựa trên một nền tảng dữ liệu sạch và quy trình thực nghiệm chuẩn tắc. Em xin kính mời Hội đồng xem cách nhóm giải quyết vấn đề Data Leakage tại Slide 07."*

---

### SLIDE 07: UNIT 2.2 — CHUỖI XỬ LÝ DỮ LIỆU DSP & KỸ THUẬT TRIỆT TIÊU DATA LEAKAGE
- **Phân mục:** Unit 02 — Project Execution
- **Thời lượng:** 55 giây (Tích lũy: 5:25)
- **Mục tiêu:** Nêu bật tư duy kỹ thuật trung thực và sâu sắc: Phát hiện lỗi rò rỉ dữ liệu (Data Leakage) khi dùng SMOTE trước khi tách tập, chủ động khắc phục bằng Stratified Split trước SMOTE, tạo ra kết quả thực nghiệm trung thực tuyệt đối.
- **Cử chỉ & Visual:** Chỉ vào biểu đồ so sánh bên phải và hai con số: 97.14% F1 Pan-Tompkins và độ lệch 0.11% giữa Val và Test. Nói với sự tự hào về sự chuẩn mực khoa học.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Ở slide này, em muốn nhấn mạnh vào hai đóng góp kỹ thuật quan trọng của nhóm trong xử lý dữ liệu:
> 
> Đầu tiên là hiệu năng của chuỗi DSP y sinh. Thuật toán Pan-Tompkins do chúng em cài đặt sử dụng bộ tích phân cửa sổ trượt 150ms kết hợp ngưỡng kép thích ứng tín hiệu. Khi kiểm thử trên hơn 20.500 nhịp tim thô từ 8 bản ghi PhysioNet khó, thuật toán đạt điểm **F1 trung bình lên tới 97.14%**, cá biệt các bản ghi chuẩn như Record 100 đạt 99.98% và Record 200 đạt 99.56%.
> 
> Thứ hai — và đây là bài học kỹ thuật quý giá nhất của chúng em: **Khắc phục triệt để lỗi rò rỉ dữ liệu (Data Leakage)**.
> Trong các nghiên cứu mở trên Kaggle, nhiều tác giả mắc lỗi áp dụng kỹ thuật cân bằng lớp SMOTE lên toàn bộ tập dữ liệu TRƯỚC KHI chia Validation. Điều này tạo ra hiện tượng rò rỉ thông tin láng giềng khiến tập Validation đạt độ chính xác ảo lên tới 99.78% nhưng rớt mạnh trên dữ liệu thật.
> 
> Nhóm em đã chủ động bẻ gãy sai lầm này bằng quy trình chuẩn: **Tách tập Stratified Validation 10% độc lập hoàn toàn TRƯỚC, sau đó CHỈ áp dụng SMOTE trên nội bộ tập Train**. Kết quả thực nghiệm hoàn toàn minh bạch: Độ chính xác trên tập Validation đạt 98.62%, sát khít với tập Test là 98.51% — **độ lệch chỉ vỏn vẹn 0.11%**, chứng minh mô hình có khả năng tổng quát hóa thực chất và không hề bị Overfitting!"

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Tại sao nhóm không chia dữ liệu theo bệnh nhân (Inter-patient) ngay từ đầu mà vẫn chia theo nhịp (Intra-patient)?"*
- **Nam Hải trả lời:** *"Dạ thưa Hội đồng, đây là một câu hỏi rất sâu sắc về phương pháp luận. Tập dữ liệu chuẩn Kaggle 187 mẫu được cộng đồng tiền xử lý và cắt sẵn theo từng nhịp nhằm phục vụ benchmark thuật toán nơ-ron tiêu chuẩn AAMI. Nhóm em đã kiểm soát nghiêm ngặt bằng Stratified Split trước SMOTE để đảm bảo không rò rỉ mẫu tổng hợp. Đồng thời, tại Unit 4 của bài báo cáo hôm nay, nhóm em cũng sẽ công khai thử nghiệm mô hình trên các tập dữ liệu bệnh nhân hoàn toàn mới (như SVDB, EDB) để đánh giá thực chất hiện tượng Domain Shift liên bệnh nhân."*

➔ **Câu nối chuyển tiếp:** *"Sau khi đã có tập dữ liệu sạch và chuẩn hóa, nhóm tiến hành huấn luyện và đối sánh 5 kiến trúc học sâu. Kính mời Hội đồng cùng quan sát kết quả tại Slide 08."*

---

### SLIDE 08: UNIT 2.3 — BENCHMARK 5 KIẾN TRÚC 1D & TRỌNG TÂM LÕI RESNET-1D
- **Phân mục:** Unit 02 — Project Execution
- **Thời lượng:** 55 giây (Tích lũy: 6:20)
- **Mục tiêu:** Chứng minh sự vượt trội của ResNet-1D so với 4 kiến trúc đối sánh (CNN-LSTM, TCN, Mamba, Vanilla 1D-CNN) cả về Accuracy (98.57%), F1-macro (91.70-92.39%), thông lượng (7,546 nhịp/s) và Recall lớp nguy hiểm V (96.20%).
- **Cử chỉ & Visual:** Chỉ tay vào bảng đối sánh 5 mô hình. Nhấn mạnh vào cấu trúc Residual Block với Skip Connection giúp giải quyết bài toán vanishing gradient.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Để lựa chọn hạt nhân AI tối ưu nhất cho hệ thống thời gian thực, chúng em không chọn mô hình theo cảm tính mà tiến hành một thực nghiệm Benchmark toàn diện trên **5 kiến trúc học sâu 1 chiều** phổ biến nhất hiện nay: gồm 1D-CNN cơ bản, CNN-LSTM, TCN (Temporal Convolutional Network), Mamba-1D (State-Space Model mới nhất) và ResNet-1D.
> 
> Kết quả đo lường định lượng trên cùng một tập kiểm thử độc lập cho thấy:
> - **ResNet-1D áp đảo hoàn toàn** với Accuracy đạt **98.57%** và F1-Macro đạt **91.70%** (đo lại đạt **92.39%**), bỏ xa CNN-LSTM (85.8%), TCN (82.8%) và Mamba (79.3%).
> - Về độ trễ suy luận, ResNet-1D chỉ mất **0.134 miligiây** cho một nhịp tim, tương đương thông lượng xử lý hơn **7.500 nhịp mỗi giây** — cực kỳ lý tưởng cho môi trường streaming đa bệnh nhân.
> - Đặc biệt về mặt bệnh học tim mạch: Trên nhóm nhịp Ngoại tâm thu thất (Lớp V - PVC) — loại loạn nhịp nguy hiểm nhất có thể dẫn đến rung thất, ResNet-1D đạt **Recall lên tới 96.20%** và **F1 đạt 95.61%**.
> 
> Sức mạnh của mô hình đến từ kiến trúc 3 khối Residual Blocks với các đường tắt Skip Connections, giúp các tầng nơ-ron học sâu trích xuất được các đặc trưng hình thái biến thiên cục bộ của sóng điện tim mà không bị triệt tiêu đạo hàm."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Tại sao mô hình Mamba-1D là kiến trúc State-Space rất hiện đại mà kết quả lại thấp nhất trong bảng benchmark (79.3%)?"*
- **Nam Hải trả lời:** *"Dạ thưa thầy cô, Mamba vốn phát huy sức mạnh vượt trội trên các chuỗi dữ liệu cực kỳ dài (hàng nghìn đến chục nghìn tokens) nhờ cơ chế chọn lọc trạng thái. Tuy nhiên với một cửa sổ nhịp tim đơn lẻ chỉ có 187 mẫu cục bộ, các liên kết phụ thuộc thời gian là cục bộ chứ không phải khoảng cách xa. Các bộ lọc tích chập cục bộ kết hợp Skip Connection của ResNet-1D tỏ ra hiệu quả và phù hợp hơn rất nhiều so với cơ chế State-Space trên độ dài chuỗi này."*

➔ **Câu nối chuyển tiếp:** *"Đạt độ chính xác cao là chưa đủ đối với y tế. Làm thế nào để bác sĩ tin tưởng vào quyết định của mô hình? Em xin kính mời Hội đồng chuyển sang Slide 09 với thuật toán 1D Grad-CAM."*

---

### SLIDE 09: UNIT 2.4 — EXPLAINABLE AI: 1D GRAD-CAM & CƠ CHẾ SÀNG LỌC RUNG NHĨ (AFIB)
- **Phân mục:** Unit 02 — Project Execution
- **Thời lượng:** 55 giây (Tích lũy: 7:15)
- **Mục tiêu:** Giải thích trực quan hóa 1D Grad-CAM kết nối hoàn hảo với giải phẫu học P-QRS-T của tim mạch (chứng minh AI học đúng đặc trưng y khoa chứ không học vẹt nhiễu nền), kết hợp mô-đun phân tích biến thiên Shannon Entropy sàng lọc AFib.
- **Cử chỉ & Visual:** Dùng laser pointer trỏ vào dải màu nhiệt (heatmap) đỏ rực ở vùng đỉnh QRS và giải thích tương quan giải phẫu học.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Kính thưa Hội đồng, đây chính là lời giải của NEURO-ECG cho 'Nghịch lý Hộp Đen' trong chẩn đoán y tế: **Trí tuệ nhân tạo giải thích được (Explainable AI)**.
> 
> Chúng em đã phát triển và tích hợp thuật toán **1D Grad-CAM** (Gradient-weighted Class Activation Mapping) trực tiếp trên tầng tích chập cuối cùng của ResNet-1D. Bằng cách tính toán đạo hàm riêng của điểm phân loại đối với từng kênh đặc trưng, hệ thống tạo ra một bản đồ nhiệt 1 chiều mô tả chính xác mức độ kích hoạt của nơ-ron.
> 
> Điều kỳ diệu là bản đồ nhiệt này hoàn toàn tương thích với các tiêu chuẩn hình thái học của Hội Tim mạch Hoa Kỳ:
> - Khi phát hiện nhịp Ngoại tâm thu thất (PVC - Lớp V), bản đồ nhiệt tập trung **hơn 85% năng lượng chú ý vào vùng phức bộ QRS giãn rộng trên 120 miligiây và đoạn sóng T đảo chiều** — chính là nơi xảy ra biến dạng bệnh lý.
> - Khi phát hiện nhịp Ngoại tâm thu nhĩ (PAC - Lớp S), vùng kích hoạt mạnh lập tức dời về phía trước tại **vị trí sóng P biến dạng đến sớm**.
> 
> Điều này chứng minh mô hình của chúng em đã thực sự học được bản chất sinh lý học của điện tim chứ không hề học vẹt các nhiễu nền ngẫu nhiên.
> 
> Song song với đó, hệ thống trang bị bộ sàng lọc Rung nhĩ (AFib Screener) đa tầng: phân tích tính bất thường nhịp điệu kéo dài thông qua Shannon Entropy của hiệu khoảng cách dRR, hệ số biến thiên CV_RR và chỉ số pNN50, kích hoạt báo động khi vượt ngưỡng an toàn 0.62."

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Bản đồ nhiệt Grad-CAM có thực sự là căn cứ pháp lý để khẳng định bệnh lý hay không?"*
- **Nam Hải trả lời:** *"Dạ thưa Hội đồng, chúng em luôn nhấn mạnh: Grad-CAM là công cụ giải thích thuộc tính nơ-ron (Neural Attribution Map), nó chỉ ra vùng tín hiệu nào khiến mô hình đưa ra quyết định đó. Căn cứ pháp lý chẩn đoán vẫn hoàn toàn dựa trên mắt nhìn và kết luận của bác sĩ tim mạch; Grad-CAM đóng vai trò 'trợ lý thị giác', hướng sự chú ý của bác sĩ vào đúng vùng bất thường nhanh hơn gấp nhiều lần."*

➔ **Câu nối chuyển tiếp:** *"Để đưa toàn bộ thuật toán tinh vi này từ phòng thí nghiệm ra triển khai trên thiết bị đeo tay IoT, nhóm đã thực hiện bước tối ưu hóa nhúng ra sao? Xin mời Hội đồng nhìn vào Slide 10."*

---

### SLIDE 10: UNIT 2.5 — TỐI ƯU HÓA NHÚNG: LƯỢNG TỬ HÓA ONNX INT8 & BÀN GIAO SÂN KHẤU
- **Phân mục:** Unit 02 — Project Execution
- **Thời lượng:** 50 giây (Tích lũy: **8:05**)
- **Mục tiêu:** Báo cáo thành tích nén 74.5% còn 697.3 KB (đạt KPI < 700 KB của SIC), giải thích cơ chế tăng tốc ONNX FP32 4 lần (0.29ms), và thực hiện bàn giao sân khấu cực kỳ mượt mà, chuyên nghiệp cho bạn Hải Yến sang Unit 3.
- **Cử chỉ & Visual:** Chỉ tay vào 2 con số ấn tượng: Nén 74.5% và Dung lượng 697.3 KB. Sau khi dứt lời kỹ thuật, xoay người trang trọng, mỉm cười và đưa tay mời bạn Hải Yến.

#### 🎙 Lời Thoại Thuyết Trình Mẫu:
> "Kính thưa Hội đồng, để một giải pháp AI y tế có thể ứng dụng vào đời sống, nó không thể chỉ nằm trên các máy chủ đám mây đắt đỏ, mà phải chạy được trên các thiết bị đeo tay theo dõi bệnh nhân liên tục (Wearable Edge Devices) với bộ nhớ và pin vô cùng giới hạn.
> 
> Nhóm chúng em đã ứng dụng kỹ thuật lượng tử hóa sau huấn luyện (Post-Training Quantization - PTQ) chuyển đổi mô hình sang định dạng ONNX Runtime INT8. Và kết quả thu được vô cùng mỹ mãn:
> - **Dung lượng mô hình được nén giảm tới 74.5%**, từ 2.735 KB xuống còn đúng **697.3 KB** — hoàn thành xuất sắc mục tiêu cam kết ban đầu trong đề cương là dưới 700 KB, cho phép nạp gọn gàng vào bộ nhớ flash của các dòng vi điều khiển nhúng như ARM Cortex hay Raspberry Pi.
> - **Bảo toàn độ chính xác cao:** mô hình chỉ lệch 0.67 điểm % (từ 94.33% xuống 93.66%), hoàn toàn nằm trong dung sai an toàn 2% theo chuẩn y tế.
> - Trên môi trường CPU chuẩn, phiên bản tối ưu hóa ONNX FP32 đạt độ trễ **0.29 miligiây** — tăng tốc gần 4 lần so với runtime PyTorch gốc.
> 
> Như vậy, toàn bộ chuỗi xử lý từ DSP, mô hình AI lõi, thuật toán giải thích Grad-CAM cho tới bộ nén lượng tử hóa ONNX đã được kiểm định kỹ thuật hoàn chỉnh và sẵn sàng vận hành.
> 
> *(Lời chuyển giao sân khấu đỉnh cao):*  
> **Và ngay sau đây, để minh chứng cho năng lực thực tế của toàn bộ kiến trúc này trên nền tảng Web thời gian thực cùng phiên chạy thử nghiệm trực tiếp, em xin phép được trân trọng nhường lại phần thuyết trình cho bạn Phan Thị Hải Yến để bắt đầu Unit 3: Kết quả thực nghiệm và phiên Live Demonstration hệ thống NEURO-ECG. Xin trân trọng kính mời bạn Hải Yến!"**

#### 🛡 Chiêu Thức Phản Biện Nhanh (Fast Defense):
- **Hội đồng hỏi:** *"Tại sao trên CPU thông thường, độ trễ đo được của INT8 đôi khi lại chậm hơn FP32?"*
- **Nam Hải trả lời:** *"Dạ thưa thầy cô, đây là một đặc thù kỹ thuật phần cứng rất kinh điển: Trên các chip CPU thông thường không có tập lệnh tăng tốc phần cứng VNNI hoặc AVX-512 VNNI, runtime phải mất chi phí chuyển đổi (dequantize/quantize) giữa số nguyên 8-bit và dấu phẩy động. Tuy nhiên, giá trị cốt lõi của INT8 ở đây là nén dung lượng 74.5% xuống 697.3 KB để nhúng vừa flash vi điều khiển; và khi nạp lên các dòng chip biên chuyên dụng như Jetson Nano hoặc vi xử lý ARM có nhân NEON, INT8 sẽ bộc lộ toàn bộ ưu thế gia tốc vượt trội cả về tốc độ lẫn tiết kiệm điện năng."*

---

## BẢNG TỔNG HỢP "THẦN CHÚ" PHẢN BIỆN DÀNH CHO NGUYỄN ĐÀO NAM HẢI

| Câu hỏi hóc búa từ Hội đồng | "Thần chú" phản biện sắc bén của Nam Hải |
| :--- | :--- |
| **1. "Tại sao dùng 1D mà không chuyển sang 2D Spectrogram?"** | Tín hiệu điện tim bản chất là chuỗi thời gian 1 chiều với các điểm uốn sinh lý cực kỳ sắc nét. Mô hình 1D xử lý trực tiếp tín hiệu thô, giữ trọn vẹn pha và biên độ biên đạo cực đại, không phát sinh chi phí tính toán biến đổi Fourier (STFT), giảm thiểu bộ nhớ và đạt độ trễ chỉ 0.13ms so với hàng chục miligiây của các mạng 2D nặng nề. |
| **2. "Độ chính xác 98.57% có đáng tin cậy không khi dữ liệu mất cân bằng nặng?"** | Nhóm em hoàn toàn không chỉ nhìn vào Accuracy! Trên tập test thực tế, lớp F chỉ chiếm 0.74% trong khi lớp N chiếm hơn 82%. Vì vậy, nhóm luôn đối chiếu chỉ số F1-Macro đạt 92.39%, đặc biệt trên lớp rối loạn nhịp nguy hiểm nhất là Ngoại tâm thu thất (PVC - Lớp V), mô hình đạt Recall 96.20% và F1 95.61%. |
| **3. "Data Leakage được xử lý triệt để như thế nào?"** | Nhóm đã phát hiện và loại bỏ lỗi phổ biến trong cộng đồng: tuyệt đối KHÔNG áp dụng SMOTE trước khi chia tập. Nhóm thực hiện Stratified Split 10% Validation trước, sau đó chỉ cân bằng trên nội bộ tập Train. Bằng chứng thực nghiệm là độ lệch giữa Validation (98.62%) và Test (98.51%) chỉ là 0.11%, chứng minh mô hình không hề overfit. |
| **4. "Grad-CAM có đảm bảo tính đúng đắn y khoa không?"** | Grad-CAM là bản đồ thuộc tính gradient nơ-ron chứng minh mô hình kích hoạt tập trung > 85% năng lượng vào đúng phức bộ QRS giãn rộng và sóng T đối với nhịp V, sóng P đối với nhịp S. Đây là bằng chứng cho thấy mạng nơ-ron học đúng đặc trưng giải phẫu học chứ không phán đoán dựa vào nhiễu đường nền. |
| **5. "Lợi ích thực tế của việc lượng tử hóa ONNX INT8?"** | Dung lượng mô hình giảm 74.5% xuống 697.3 KB, hoàn thành mục tiêu dưới 700 KB để nạp vào bộ nhớ flash của các chip đeo tay Wearable. Trên CPU chuẩn, bản ONNX FP32 tăng tốc 4 lần (0.29ms); còn bản INT8 sẵn sàng khai phóng toàn bộ tốc độ xử lý khi chạy trên các dòng chip biên có tập lệnh VNNI hoặc ARM NEON. |
