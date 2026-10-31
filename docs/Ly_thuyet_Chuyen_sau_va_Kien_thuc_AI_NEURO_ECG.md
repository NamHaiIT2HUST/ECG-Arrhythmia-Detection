# BÁCH KHOA TOÀN THƯ LÝ THUYẾT VÀ KIẾN THỨC CHUYÊN SÂU AI & Y SINH
## HỆ THỐNG GIÁM SÁT ECG THỜI GIAN THỰC NEURO-ECG
**Chương trình:** Samsung Innovation Campus (SIC) 2026 — Đại học Bách khoa Hà Nội  
**Tác giả & Báo cáo viên:** Nguyễn Đào Nam Hải (Team Leader — Đảm nhiệm thuyết trình toàn bộ từ đầu đến cuối)

---

# MỤC LỤC TỔNG QUAN

1. **BẢN CHẤT SINH LÝ HỌC ĐIỆN TIM & BỆNH HỌC RỐI LOẠN NHỊP (CARDIAC PHYSIOLOGY & PATHOLOGY)**
   - Cơ chế điện thế hoạt động cơ tim (Cardiac Action Potential).
   - Giải phẫu phức bộ P-QRS-T và ý nghĩa sinh học từng đoạn sóng.
   - Chuẩn phân loại 5 nhóm nhịp AAMI EC57 (N, S, V, F, Q).
   - Cơ chế phát sinh rối loạn nhịp: Ngoại tâm thu thất (PVC), Ngoại tâm thu nhĩ (PAC), Rung nhĩ (AFib).

2. **XỬ LÝ TÍN HIỆU SỐ Y SINH (BIOMEDICAL DSP) & THUẬT TOÁN PAN-TOMPKINS**
   - Các nguồn tạp âm điện tim: Nhiễu thở, nhiễu điện lưới 50Hz, nhiễu cơ EMG.
   - Thiết kế bộ lọc số: Butterworth Bandpass (0.5–45Hz) và IIR Notch (50Hz, Q=30).
   - Thuật toán Pan-Tompkins QRS: Vi phân, bình phương, tích phân cửa sổ trượt (MWI 150ms), ngưỡng kép thích nghi động.
   - Phép biến đổi Resampling Polyphase chuyển đổi tần số từ 360Hz sang 125Hz (187 điểm).

3. **KHẢO SÁT & ĐỐI SÁNH TOÀN DIỆN 5 KIẾN TRÚC MẠNG HỌC SÂU 1D**
   - Tại sao chọn xử lý 1D trực tiếp mà không chuyển sang 2D Spectrogram (STFT/CWT)?
   - Kiến trúc 1: ResNet-1D (Residual Blocks, Skip Connections, Receptive Field, Batch Normalization).
   - Kiến trúc 2: CNN1D-LSTM (Cơ chế không gian - thời gian, Vanishing Gradient của RNN, Gate Mechanics).
   - Kiến trúc 3: TCN (Temporal Convolutional Network, Dilated Causal Convolution, Tốc độ tiếp nhận $2^d \cdot k$).
   - Kiến trúc 4: Transformer-1D (Cơ chế Self-Attention $\mathcal{O}(N^2)$, Thiếu Inductive Bias cục bộ).
   - Kiến trúc 5: Mamba-1D (State Space Model - SSM, Phép rời rạc hóa ZOH, Lý do underperform trên chuỗi 187 điểm).
   - Bảng phân tích định lượng 5 mô hình: Tham số, Độ trễ (Latency), Thông lượng (Throughput), F1-Macro, Recall từng lớp bệnh lý.

4. **TẠI SAO RESNET-1D CHIẾN THẮNG TUYỆT ĐỐI? (DEEP DIVE RESNET-1D)**
   - Inductive Bias khớp hoàn hảo với đặc trưng hình thái học ECG.
   - Giải quyết triệt để suy giảm đạo hàm (Vanishing Gradient) qua đường tắt đồng nhất (Identity Shortcut).
   - Độ phức tạp tính toán tối ưu: 692k tham số, forward 0.133 ms/nhịp, thông lượng 7.546 nhịp/giây.
   - Năng lực phát hiện nhịp nguy cấp: Recall lớp V đạt 96.20% – 97.30%.

5. **KỸ THUẬT DỮ LIỆU, MẤT CÂN BẰNG LỚP & SỬA LỖI DATA LEAKAGE**
   - Nghịch lý mất cân bằng lớp y tế (Lớp N 82.8% vs Lớp F 0.74%).
   - Cơ chế thuật toán SMOTE (Nội suy láng giềng k-NN).
   - **Lỗ hổng chí mạng Data Leakage trên Kaggle**: Áp dụng SMOTE trước khi chia tập gây ảo giác Acc 99.78%.
   - Quy trình chuẩn của nhóm: Stratified Split 10% Validation trước SMOTE -> Độ lệch Val-Test chỉ 0.11%.
   - Phân biệt mô hình Intra-patient vs Inter-patient (de Chazal protocol).

6. **LÝ THUYẾT TRÍ TUỆ NHÂN TẠO GIẢI THÍCH ĐƯỢC (1D GRAD-CAM & XAI)**
   - Tại sao Black-box AI bị từ chối trong y tế (Quy chuẩn FDA/MDR cho SaMD).
   - Công thức toán học 1D Grad-CAM: Đạo hàm riêng, Trọng số kích hoạt nơ-ron $\alpha_k^c$, Hàm ReLU cắt bỏ âm tính.
   - Tương quan lâm sàng của Heatmap: Khớp chính xác với sóng P biến dạng (PAC) và phức bộ QRS giãn rộng (PVC).

7. **LÝ THUYẾT LƯỢNG TỬ HÓA & TỐI ƯU HÓA EDGE AI (ONNX RUNTIME INT8)**
   - Biểu diễn số học FP32 vs INT8.
   - Kỹ thuật Lượng tử hóa sau huấn luyện (Post-Training Quantization - PTQ): Scale $S$ và Zero-point $Z$.
   - Nén 74.5% dung lượng (2.735 KB -> 697.3 KB) thỏa mãn tiêu chuẩn nhúng < 700 KB.
   - Nghịch lý độ trễ INT8 trên CPU thông thường và lợi thế trên phần cứng chuyên dụng (VNNI, AVX-512, ARM NEON).

8. **CƠ CHẾ SÀNG LỌC RUNG NHĨ (AFIB SCREENING VIA STATISTICAL & SHANNON ENTROPY)**
   - Cơ chế bệnh lý Rung nhĩ: Mất sóng P, nhịp thất không đều hoàn toàn (Irregularly Irregular).
   - Các đại lượng thống kê: $\Delta RR$, $CV_{RR}$, $RMSSD$, $pNN50$.
   - Shannon Entropy của phân phối khoảng cách nhịp tim $H(\Delta RR)$.
   - Hệ thống chấm điểm đa quy tắc và ngưỡng kích hoạt 0.62.

9. **HIỆN TƯỢNG DỊCH CHUYỂN MIỀN DỮ LIỆU (DOMAIN SHIFT) & KỸ THUẬT THÍCH NGHI (FINE-TUNING)**
   - Sự sụt giảm hiệu năng khi kiểm thử ngoại kiểm trên SVDB, EDB.
   - Nguyên nhân gốc rễ: Khác biệt đạo trình đo (MLII vs Lead II/V5), khác biệt phần cứng và quần thể bệnh nhân.
   - Kết quả thực nghiệm Fine-tuning trên INCART: Tăng vọt từ 85.94% lên 93.18%.

10. **HẠ TẦNG PHẦN MỀM Y TẾ, TIÊU CHUẨN IEC 60601-1-8 & HUMAN-IN-THE-LOOP**
    - Kiến trúc vi dịch vụ hướng sự kiện (Event-driven FastAPI + WebSocket 360Hz).
    - Mẫu thiết kế Singleton Pattern loại bỏ Garbage Collection jitter.
    - Tiêu chuẩn cảnh báo y tế IEC 60601-1-8 (Phân tầng màu sắc, âm báo, chức năng tạm tắt chuông 120s).
    - Cơ chế RBAC 3 vai trò và Bảng Audit Trail lưu vết pháp lý y khoa.

---

# CHI TIẾT NỘI DUNG 10 CHỦ ĐỀ CHUYÊN SÂU

---

## 1. BẢN CHẤT SINH LÝ HỌC ĐIỆN TIM & BỆNH HỌC RỐI LOẠN NHỊP

### 1.1. Cơ chế Điện thế hoạt động tim mạch (Cardiac Action Potential)
Tín hiệu điện tim (ECG) là đồ thị ghi lại biến thiên hiệu điện thế phát sinh do quá trình khử cực (depolarization) và tái cực (repolarization) của hàng triệu tế bào cơ tim theo thời gian.
- **Nút xoang (SA Node):** Đóng vai trò máy tạo nhịp tự nhiên, phát xung điện với tần số 60–100 nhịp/phút.
- **Dẫn truyền:** Xung điện lan truyền qua tâm nhĩ $\rightarrow$ Nút nhĩ thất (AV Node - làm chậm tín hiệu 0.1s để máu kịp xuống thất) $\rightarrow$ Bó His $\rightarrow$ Nhánh mạng Purkinje $\rightarrow$ Cơ tâm thất.

### 1.2. Giải phẫu phức bộ P-QRS-T
```
             R (Đỉnh R - Đỉnh nhọn biên độ cao nhất)
            / \
           /   \
    P     /     \       T (Sóng T - Tái cực thất)
   _/\_  /       \     _/\_
 _/    \/         \___/    \_
       Q           S
 |  PR  |   QRS   |    ST   |
 |      QT Interval         |
```
1. **Sóng P:** Đại diện cho sự **khử cực của 2 tâm nhĩ**. Thời gian bình thường: $< 120\text{ ms}$, biên độ $< 0.25\text{ mV}$.
2. **Khoảng PR:** Thời gian dẫn truyền từ nhĩ qua nút nhĩ thất đến thất. Bình thường: $120 - 200\text{ ms}$.
3. **Phức bộ QRS:** Đại diện cho sự **khử cực của 2 tâm thất**. Đây là cấu trúc có năng lượng và độ dốc (slope) lớn nhất trên ECG:
   - Sóng Q: Sóng âm đầu tiên.
   - Sóng R: Sóng dương nhọn cao.
   - Sóng S: Sóng âm sau sóng R.
   - Thời gian QRS bình thường: $60 - 100\text{ ms}$ (nhỏ hơn 120 ms).
4. **Đoạn ST:** Giai đoạn tâm thất co bóp đẳng thế. Rất quan trọng trong chẩn đoán nhồi máu cơ tim (ST chênh lên/chênh xuống).
5. **Sóng T:** Đại diện cho sự **tái cực của 2 tâm thất**.

### 1.3. Chuẩn phân loại 5 nhóm nhịp AAMI EC57
Hiệp hội Thiết bị Y tế vì Sự tiến bộ (AAMI) ban hành tiêu chuẩn ANSI/AAMI EC57:1998 chia nhịp tim thành 5 lớp lớn:
1. **Lớp N (Normal / Non-ectopic):** Nhịp bình thường, nhịp xoang, Block nhánh trái/phải (LBBB, RBBB).
2. **Lớp S (Supraventricular Ectopic Beat - SVEB):** Nhịp ngoại vị trên thất: Ngoại tâm thu nhĩ (PAC), nhịp bộ nối sớm, nhịp nhanh trên thất.
3. **Lớp V (Ventricular Ectopic Beat - VEB):** Nhịp ngoại vị thất: Ngoại tâm thu thất (PVC), nhịp thoát thất. **Đây là nhóm nhịp nguy hiểm nhất**, có nguy cơ khởi phát Rung thất (Ventricular Fibrillation) gây ngừng tuần hoàn đột tử.
4. **Lớp F (Fusion Beat):** Nhịp hợp nhất giữa xung động bình thường từ nhĩ và ổ ngoại vị ở thất.
5. **Lớp Q (Unknown / Paced Beat):** Nhịp máy tạo nhịp hoặc nhịp không xác định được.

---

## 2. XỬ LÝ TÍN HIỆU SỐ Y SINH (BIOMEDICAL DSP) & PAN-TOMPKINS

### 2.1. Bản chất các nguồn nhiễu trên ECG
- **Nhiễu trôi đường nền (Baseline Wander):** Tần số cực thấp ($0.05 - 0.5\text{ Hz}$), sinh ra do bệnh nhân hít thở, lồng ngực di động hoặc mồ hôi làm thay đổi điện trở tiếp xúc giữa da và điện cực.
- **Nhiễu điện lưới xoay chiều (Powerline Interference):** Tần số chính xác $50\text{ Hz}$ (tại Việt Nam/Châu Âu) hoặc $60\text{ Hz}$ (tại Mỹ), do cảm ứng từ trường từ hệ thống dây dẫn và thiết bị điện xung quanh.
- **Nhiễu cơ (Electromyogram - EMG):** Dải tần rộng ($20 - 500\text{ Hz}$), sinh ra do cơ bắp người bệnh cử động, run rẩy hoặc căng cơ.

### 2.2. Thiết kế bộ lọc số y sinh
1. **Bộ lọc thông dải Butterworth (Bandpass 0.5 – 45 Hz):**
   - Đáp ứng tần số phẳng tối đa ở dải thông (Maximally Flat Passband), không gây biến dạng biên độ sóng P-QRS-T.
   - Cắt dải dưới $0.5\text{ Hz}$ để loại bỏ hoàn toàn nhiễu thở trôi nền.
   - Cắt dải trên $45\text{ Hz}$ để dập tắt phần lớn nhiễu cơ EMG tần số cao.
2. **Bộ lọc chắn dải IIR Notch (Notch Filter 50 Hz):**
   - Hàm truyền đạt thiết kế với hệ số phẩm chất cao $Q = \frac{f_0}{\Delta f} = 30$.
   - Tạo ra một hố lõm cực hẹp quanh $50\text{ Hz}$, triệt tiêu chính xác can nhiễu điện lưới mà bảo toàn năng lượng các thành phần tần số lân cận.

### 2.3. Thuật toán Pan-Tompkins (1985) — Phát hiện đỉnh R thời gian thực
Thuật toán kinh điển chuẩn vàng trong xử lý điện tim gồm 5 bước toán học:
```
Tín hiệu thô x[n] 
  ──> [Lọc dải thông 5-15Hz] 
  ──> [Bộ vi phân 5 điểm] 
  ──> [Bình phương x^2] 
  ──> [Tích phân MWI 150ms] 
  ──> [Ngưỡng kép thích ứng] ──> Đỉnh R
```
1. **Lọc dải thông dải hẹp (Bandpass 5 – 15 Hz):** Dải tần tập trung năng lượng cao nhất của phức bộ QRS, loại bỏ sóng P và sóng T.
2. **Bộ vi phân 5 điểm (Derivative):**
   $$y[n] = \frac{1}{8} \left( 2x[n] + x[n-1] - x[n-3] - 2x[n-4] \right)$$
   Lấy đạo hàm bậc nhất để phát hiện sườn dốc đứng của phức bộ QRS (độ dốc $dV/dt$ lớn nhất).
3. **Toán tử bình phương (Squaring Operation):**
   $$y[n] = (x[n])^2$$
   Làm dương hóa toàn bộ tín hiệu và khuếch đại phi tuyến các đỉnh biên độ lớn, đè bẹp các sóng nhỏ còn sót lại.
4. **Tích phân cửa sổ trượt (Moving Window Integration - MWI):**
   $$y[n] = \frac{1}{N} \sum_{i=0}^{N-1} x[n-i]$$
   Với độ dài cửa sổ $N$ tương đương $150\text{ ms}$ (khoảng 54 mẫu tại 360Hz). Bước này tạo ra một bướu năng lượng trơn bao bọc lấy toàn bộ phức bộ QRS.
5. **Ngưỡng kép thích ứng (Dual Adaptive Thresholds):**
   Duy trì 2 ngưỡng: Ngưỡng tín hiệu ($SPKI$) và Ngưỡng nhiễu ($NPKI$). Ngưỡng quyết định:
   $$THRESHOLD\_I1 = NPKI + 0.25 \times (SPKI - NPKI)$$
   Nếu trong khoảng $1.66 \times RR_{avg}$ không tìm thấy đỉnh, thuật toán kích hoạt cơ chế **Search-back** với ngưỡng thấp hơn ($THRESHOLD\_I2 = 0.5 \times THRESHOLD\_I1$) để không bỏ sót các nhịp yếu.
- **Kết quả thực nghiệm:** F1 đạt **97.14%** trên 20.546 nhịp tim của 8 bản ghi PhysioNet khó.

### 2.4. Phép biến đổi Resampling Polyphase (360Hz -> 125Hz)
- Nguồn bản ghi PhysioNet chuẩn có tần số lấy mẫu là $360\text{ Hz}$.
- Mô hình ResNet-1D được huấn luyện trên tập Kaggle chuẩn hóa ở tần số $125\text{ Hz}$ với cửa sổ độ dài cố định 187 mẫu.
- Để chuyển đổi không bị méo tín hiệu (aliasing), hệ thống sử dụng **Polyphase Filter Resampling** với tỷ lệ phân số $\frac{L}{M} = \frac{25}{72}$ ($360 \times \frac{25}{72} = 125\text{ Hz}$).
- Thuật toán nội suy cửa sổ: Cắt cửa sổ từ đỉnh R lùi về trước 70 mẫu và tiến về sau 117 mẫu (tổng 187 mẫu) ở miền 125Hz, bảo đảm đỉnh R luôn nằm ở vị trí chuẩn hóa mẫu số 70.

---

## 3. KHẢO SÁT & ĐỐI SÁNH TOÀN DIỆN 5 KIẾN TRÚC MẠNG HỌC SÂU 1D

### 3.1. Tại sao dùng mạng 1D trực tiếp mà KHÔNG dùng 2D Spectrogram?
Một câu hỏi kinh điển của các Giám khảo AI: *"Tại sao không dùng Short-Time Fourier Transform (STFT) hay Continuous Wavelet Transform (CWT) để biến tín hiệu thành ảnh quang phổ (Spectrogram) rồi dùng ResNet-2D/Vision Transformer?"*

**Lý lẽ khoa học đanh thép:**
1. **Bản chất tín hiệu:** ECG là một chuỗi điện thế biến thiên theo thời gian với các điểm uốn sắc nhọn (đỉnh R, rãnh Q, S). Biến đổi sang 2D Spectrogram làm nhòe độ phân giải thời gian (bị giới hạn bởi Nguyên lý bất định Heisenberg-Gabor $\Delta t \cdot \Delta f \ge \frac{1}{4\pi}$).
2. **Chi phí tính toán (Computational Overhead):** Biến đổi FFT/Wavelet đòi hỏi tài nguyên tính toán liên tục, làm tăng độ trễ pipeline lên hàng chục miligiây, không phù hợp cho vi điều khiển nhúng pin yếu.
3. **Kích thước mô hình:** ResNet-2D (như ResNet-18/50) có từ 11 triệu đến 25 triệu tham số ($> 45\text{ MB}$), không thể nhúng vừa bộ nhớ Flash $< 1\text{ MB}$ của vi điều khiển đeo tay. ResNet-1D chỉ cần **692k tham số** ($2.7\text{ MB}$ ở FP32 và **697 KB** ở INT8).
4. **Bảo toàn pha tín hiệu:** Mạng 1D tiếp nhận trực tiếp biên độ và cực tính (âm/dương), đây là dấu hiệu sinh lý quyết định sự đảo ngược của sóng T hay phức bộ QRS.

---

### 3.2. Chi tiết 5 kiến trúc được khảo sát trong nghiên cứu

```
                                  KIẾN TRÚC 5 MÔ HÌNH KHẢO SÁT
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. ResNet-1D:     Input(187) ──> Stem Conv ──> [ResBlock 1] ──> [ResBlock 2] ──> [ResBlock 3] ──> FC │
│                                                (Skip +32)       (Skip +64)       (Skip +128)          │
│ 2. CNN1D-LSTM:    Input(187) ──> Conv1D + MaxPool ──> Conv1D + MaxPool ──> Bi-LSTM(64) ──> FC        │
│ 3. TCN:           Input(187) ──> Dilated Conv1D (d=1,2,4,8) với Causal Padding + Skip ──> FC           │
│ 4. Transformer1D: Input(187) ──> Linear Patch Embed + PosEncoding ──> Multi-Head Attention (x2) ──> FC│
│ 5. Mamba-1D:      Input(187) ──> Linear Proj ──> Selective SSM State Expansion (d=16) ──> SiLU ──> FC  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### 1. ResNet-1D (Residual Network 1D)
- **Cấu trúc:** Stem tích chập (Conv1D $k=7, s=2$, 32 filters, MaxPool) $\rightarrow$ 3 Khối Residual Blocks (kênh tăng dần: $32 \rightarrow 64 \rightarrow 128 \rightarrow 256$, kernel $k=5$) $\rightarrow$ Global Adaptive Average Pooling $\rightarrow$ Linear Classifier (5 lớp).
- **Cơ chế cốt lõi:** Đường tắt đồng nhất (Identity Skip Connection):
  $$y = \mathcal{F}(x, \{W_i\}) + x$$
  Đạo hàm khi lan truyền ngược:
  $$\frac{\partial \mathcal{E}}{\partial x} = \frac{\partial \mathcal{E}}{\partial y} \left( \frac{\partial \mathcal{F}}{\partial x} + 1 \right)$$
  Thành phần $+1$ đảm bảo dòng gradient không bao giờ bị triệt tiêu về 0, cho phép thông tin đi xuyên suốt qua các tầng sâu.

#### 2. CNN1D-LSTM (Hybrid Spatial-Temporal Network)
- **Cấu trúc:** 2 tầng Conv1D (trích xuất đặc trưng hình thái cục bộ) $\rightarrow$ 1 tầng Bi-directional LSTM 64 units (bắt giữ quan hệ phụ thuộc thời gian tiến/lùi) $\rightarrow$ Dense Layer.
- **Nhược điểm bộc lộ:** Cơ chế tuần tự của LSTM khiến độ trễ forward bị cản trở, đồng thời các cổng (Input/Forget/Output Gate) dễ bị bão hòa gradient khi chuỗi có các biến động biên độ quá lớn. Đạt F1-Macro 85.79%, thấp hơn nhiều so với ResNet.

#### 3. TCN (Temporal Convolutional Network)
- **Cấu trúc:** Tích chập dãn nở nhân quả (Dilated Causal Convolutions) với tốc độ tăng trưởng lũy thừa của hệ số dãn nở $d \in \{1, 2, 4, 8\}$.
- **Trường tiếp nhận (Receptive Field):**
  $$RF = 1 + \sum_{l=0}^{L-1} (K_l - 1) \cdot d_l$$
- **Nhược điểm bộc lộ:** TCN cần nhiều tầng dãn nở để bao phủ cửa sổ 187 mẫu. Các phép tính tích chập dãn nở tạo ra các lỗ trống (holes) trong ma trận trọng số, làm giảm độ sắc nét khi trích xuất các đỉnh nhọn hẹp như sóng Q và R. F1-Macro đạt 82.81%.

#### 4. Transformer-1D (Vision Transformer for 1D Signals)
- **Cấu trúc:** Phân mảnh chuỗi thành các token nhỏ (patch size 11 hoặc ánh xạ điểm) $\rightarrow$ Thêm Positional Encoding $\rightarrow$ 2 khối Multi-Head Self-Attention ($d_{model}=64, n_{heads}=4$) $\rightarrow$ MLP Head.
- **Nhược điểm bộc lộ:** Độ phức tạp tính toán cơ chế Attention là bậc hai $\mathcal{O}(N^2)$. Quan trọng hơn, Transformer thiếu **Inductive Bias** (tính bất biến tịnh tiến và tính cục bộ của các phép tích chập). Với một tập dữ liệu ECG vài chục nghìn mẫu, Transformer không có đủ lượng dữ liệu khổng lồ để tự học các cấu trúc cục bộ như mạng Conv, dẫn đến F1-Macro chỉ đạt 83.11%.

#### 5. Mamba-1D (Selective State Space Model - SSM)
- **Cấu trúc:** Mô hình hóa chuỗi thời gian thông qua phương trình vi phân liên tục:
  $$h'(t) = \mathbf{A}h(t) + \mathbf{B}x(t), \quad y(t) = \mathbf{C}h(t)$$
  Rời rạc hóa thông qua phép biến đổi Zero-Order Hold (ZOH) với bước nhảy $\Delta$:
  $$\overline{\mathbf{A}} = \exp(\Delta \mathbf{A}), \quad \overline{\mathbf{B}} = (\Delta \mathbf{A})^{-1} (\exp(\Delta \mathbf{A}) - \mathbf{I}) \cdot \Delta \mathbf{B}$$
- **Tại sao Mamba-1D lại có kết quả thấp nhất (Accuracy 94.45%, F1 79.28%)?**
  *Câu hỏi này Hội đồng SIC rất hay hỏi để thử thách kiến thức chuyên sâu của bạn:*
  - **Bản chất thiết kế của Mamba:** Mamba sinh ra để khắc phục nhược điểm $\mathcal{O}(N^2)$ của Transformer trên **chuỗi cực kỳ dài** (hàng chục nghìn tokens như văn bản dài, DNA sequences, audio hàng chục giây) nhờ cơ chế quét chọn lọc tuyến tính $\mathcal{O}(N)$.
  - **Nghịch lý độ dài chuỗi:** Một nhịp tim cắt sẵn chỉ có đúng **187 điểm dữ liệu** (chuỗi siêu ngắn). Ở độ dài này, ưu thế nén bộ nhớ trạng thái không thể bù đắp được việc mất mát các đặc trưng hình thái cục bộ sắc nét.
  - Ma trận trạng thái $\mathbf{A}$ đóng vai trò như bộ nhớ trơn hóa liên tục, vô tình "làm mòn" các gai nhọn cực ngắn của đỉnh R và sóng ngoại tâm thu, khiến Recall lớp S bị rớt xuống chỉ còn 69.60%.

---

### 3.3. Bảng đối sánh kỹ thuật tổng hợp (Golden Benchmark Matrix)

| Mô hình | Số tham số | Độ trễ forward | Thông lượng | Accuracy (%) | F1-Macro (%) | Recall V (PVC) | F1-Score V |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ResNet-1D (Nhóm chọn)** | **692.389** | **0.133 ms** | **7.546 nhịp/s** | **98.43% – 98.57%** | **91.70% – 92.39%** | **96.20%** | **95.61%** |
| **CNN1D-LSTM** | 242.885 | 0.122 ms | 8.164 nhịp/s | 97.27% | 85.79% | 96.20% | 95.48% |
| **TCN** | 171.365 | 0.601 ms | 1.663 nhịp/s | 96.17% | 82.81% | 96.20% | 94.60% |
| **Transformer-1D** | 69.317 | 0.592 ms | 1.687 nhịp/s | 95.36% | 83.11% | 93.16% | 92.21% |
| **Mamba-1D** | 59.877 | 0.490 ms | 2.038 nhịp/s | 94.45% | 79.28% | 91.16% | 89.10% |

---

## 4. TẠI SAO RESNET-1D CHIẾN THẮNG TUYỆT ĐỐI?

1. **Khớp nối hoàn hảo với Inductive Bias y sinh:**
   - Các bộ lọc tích chập (Conv1D) có tính chất **Translation Equivariance** (tính bất biến đồng biến tịnh tiến). Nếu đỉnh R dịch chuyển nhẹ vài mili-giây sang trái hay sang phải do biến thiên nhịp tim, các bộ lọc vẫn bắt giữ chính xác hình thái sóng.
   - Cấu trúc phân tầng: Tầng 1 (Stem) bắt các cạnh dốc của tín hiệu; Tầng 2 (Layer 1) kết hợp thành các sóng đơn lẻ P, Q, R, S, T; Tầng 3 (Layer 2 & 3) học mối tương quan không gian giữa độ rộng QRS và chiều phân cực của sóng T.
2. **Khắc phục triệt để Degradation Problem:**
   - Nếu tăng độ sâu của mạng CNN thông thường, độ chính xác sẽ bão hòa và sụt giảm nhanh (hiện tượng suy thoái mạng chứ không phải overfitting). Các đường tắt Skip Connection của ResNet giải phóng mạng nơ-ron khỏi gánh nặng phải học ánh xạ đồng nhất từ đầu, giúp mạng dễ dàng tối ưu hóa hơn gấp nhiều lần.
3. **Cực kỳ thân thiện với phần cứng nhúng (Hardware Friendly):**
   - Chỉ gồm các phép nhân tích chập chuẩn (Standard 1D GEMM - General Matrix Multiply), không có phân nhánh điều kiện phức tạp như LSTM, không có ma trận tự chú ý động như Transformer. Điều này cho phép trình biên dịch ONNX và các tập lệnh tăng tốc phần cứng (VNNI, ARM NEON) tối ưu hóa việc phân luồng tính toán SIMD đạt hiệu suất đỉnh cao.

---

## 5. KỸ THUẬT DỮ LIỆU, MẤT CÂN BẰNG LỚP & DATA LEAKAGE

### 5.1. Bản chất phân phối mất cân bằng lớp (AAMI Imbalance)
Trong tự nhiên, một người bình thường đập khoảng 100.000 nhịp tim/ngày thì có tới hơn 95% là nhịp bình thường. Trên tập dữ liệu benchmark MIT-BIH chuẩn:
- **Lớp N (Normal):** ~82.76% (Đa số áp đảo)
- **Lớp S (PAC):** ~2.54% (Hiếm)
- **Lớp V (PVC):** ~6.61% (Nguy hiểm)
- **Lớp F (Fusion):** ~0.74% (Cực kỳ hiếm)
- **Lớp Q (Paced):** ~7.35% (Không xác định)

Nếu một mô hình AI "ngây thơ" luôn luôn đoán là lớp N, mô hình đó đã tự động đạt **Accuracy 82.76%** mà hoàn toàn vô dụng trong y tế vì bỏ sót 100% người bệnh sắp đột tử!
$\rightarrow$ **Chính vì vậy, trong y tế, chỉ số F1-Macro và Recall từng lớp bệnh lý mới là thước đo sinh tử.**

### 5.2. Lỗ hổng chí mạng "Data Leakage" phổ biến trên Kaggle
Khi khảo sát hàng trăm notebook trên Kaggle xử lý bộ dữ liệu `mitbih_train.csv`, nhóm phát hiện một sai lầm phương pháp luận nghiêm trọng:
```
[SAI LẦM PHỔ BIẾN]:
Dữ liệu thô ──> [Áp dụng SMOTE cân bằng lớp] ──> [Chia Train / Validation (80/20)]
                                                         ▲
                                           (RÒ RỈ DỮ LIỆU CỰC KỲ NẶNG!)
```
- **Tại sao lại rò rỉ?** Thuật toán SMOTE hoạt động bằng cách tìm $k$ láng giềng gần nhất của mẫu thiểu số và tạo ra các điểm dữ liệu tổng hợp nằm trên đoạn thẳng nối giữa 2 mẫu đó:
  $$x_{new} = x_i + \lambda (x_{zi} - x_i), \quad \lambda \in [0, 1]$$
- Nếu áp dụng SMOTE trước khi chia tập, các mẫu tổng hợp được tạo ra từ thông tin láng giềng của các mẫu sau đó lại bị đưa vào tập Validation! Mô hình thực chất đã "nhìn thấy trước đề thi" thông qua các mẫu nhân bản láng giềng, dẫn đến điểm **Validation Accuracy ảo lên tới 99.78%**. Khi đem mô hình này kiểm thử trên tập Test thực tế hoặc dữ liệu bệnh viện thì độ chính xác rớt thảm hại.

### 5.3. Quy trình chuẩn mực của nhóm NEURO-ECG
```
[QUY TRÌNH CHUẨN MỰC CỦA NHÓM]:
Dữ liệu thô ──> [Stratified Split 10% Validation] ──┬──> [Validation Set 10%] (Bảo mật tuyệt đối)
                                                    │
                                                    └──> [Áp dụng SMOTE CHỈ TRÊN TẬP TRAIN 90%]
```
- **Kết quả thực nghiệm minh chứng:**
  - Tập Validation độc lập đạt: **98.62%**
  - Tập Test chính thức đạt: **98.51%**
  - **Độ lệch chỉ 0.11%** $\rightarrow$ Bằng chứng khoa học không thể chối cãi chứng minh mô hình học thực chất, không overfit và hoàn toàn sạch bóng Data Leakage!

---

## 6. LÝ THUYẾT TRÍ TUỆ NHÂN TẠO GIẢI THÍCH ĐƯỢC (1D GRAD-CAM)

### 6.1. Tại sao AI Y tế bắt buộc phải có XAI?
Theo đạo luật EU AI Act và hướng dẫn của FDA đối với Phần mềm Thiết bị Y tế (SaMD - Software as a Medical Device):
- Các mô hình học máy cấp độ rủi ro cao (như chẩn đoán tim mạch) không được phép là "Hộp đen" (Black-Box).
- Bác sĩ chịu trách nhiệm pháp lý cao nhất đối với sinh mạng người bệnh. Nếu AI báo "Nhịp thất V" mà không có căn cứ giải phẫu, bác sĩ không thể tiêm thuốc chống loạn nhịp (như Amiodarone hay Lidocaine) vì nguy cơ tác dụng phụ nguy hiểm.

### 6.2. Công thức toán học 1D Grad-CAM
Grad-CAM (Gradient-weighted Class Activation Mapping) mở rộng cho chuỗi tín hiệu 1 chiều:
1. Cho mô hình nơ-ron nhận đầu vào $x$, tính toán điểm số dự đoán chưa chuẩn hóa (logits) $y^c$ cho lớp bệnh lý mục tiêu $c$.
2. Xét tầng tích chập cuối cùng (Layer 3 của ResNet-1D), gồm $K = 256$ kênh đặc trưng, mỗi kênh là một chuỗi 1D có chiều dài $L = 24$. Ký hiệu ma trận đặc trưng là $A^k \in \mathbb{R}^L$.
3. Tính toán đạo hàm riêng của điểm số $y^c$ đối với từng điểm vị trí $i$ trên kênh đặc trưng $k$:
   $$\frac{\partial y^c}{\partial A_i^k}$$
4. Tính toán trọng số tầm quan trọng (Neuron Importance Weight) $\alpha_k^c$ bằng phép lấy trung bình toàn cục (Global Average Pooling 1D):
   $$\alpha_k^c = \frac{1}{L} \sum_{i=1}^L \frac{\partial y^c}{\partial A_i^k}$$
   Trọng số $\alpha_k^c$ biểu thị mức độ đóng góp của toàn bộ kênh $k$ vào việc quyết định lớp $c$.
5. Kết hợp tuyến tính các kênh đặc trưng theo trọng số và áp dụng hàm chỉnh lưu tuyến tính ReLU:
   $$L_{Grad-CAM}^c = \text{ReLU}\left( \sum_{k=1}^K \alpha_k^c A^k \right)$$
   Hàm $\text{ReLU}$ có vai trò sống còn: chỉ giữ lại các đặc trưng có tác động tích cực (làm tăng điểm số của lớp $c$), triệt tiêu các đặc trưng làm giảm điểm số.
6. Nội suy (Interpolation) bản đồ $L_{Grad-CAM}^c$ từ độ dài $L=24$ trở lại độ dài gốc 187 điểm và chuẩn hóa Min-Max về thang $[0, 1]$.

### 6.3. Tương quan sinh lý học thực chứng
- **Đối với nhịp V (Ngoại tâm thu thất - PVC):** Bản đồ nhiệt tập trung **> 85% năng lượng màu đỏ** vào vùng phức bộ QRS bị giãn rộng ($> 120\text{ ms}$) và đoạn sóng T đảo cực. Đây chính là tiêu chuẩn vàng chẩn đoán của Hội Tim mạch Hoa Kỳ (AHA) cho thấy cơ thất bị kích hoạt bất thường lạc chỗ.
- **Đối với nhịp S (Ngoại tâm thu nhĩ - PAC):** Bản đồ nhiệt kích hoạt mạnh mẽ tại **vị trí sóng P đến sớm**, phản ánh ổ phát nhịp bất thường nằm ở cơ nhĩ trước khi đi qua nút nhĩ thất.

---

## 7. LÝ THUYẾT LƯỢNG TỬ HÓA & TỐI ƯU HÓA EDGE AI (ONNX INT8)

### 7.1. Bản chất Lượng tử hóa số học (Quantization)
Mô hình huấn luyện PyTorch lưu trữ trọng số dưới dạng số thực dấu phẩy động 32-bit (FP32 - IEEE 754):
- 1 bit dấu, 8 bit phần mũ, 23 bit phần định trị (chiếm 4 bytes bộ nhớ).
- Lượng tử hóa INT8 ánh xạ các số thực FP32 trong khoảng $[x_{min}, x_{max}]$ về không gian số nguyên 8-bit có dấu $[-128, 127]$ (chiếm đúng 1 byte bộ nhớ $\rightarrow$ tự động giảm 75% dung lượng lưu trữ lý thuyết).

Công thức ánh xạ lượng tử hóa tuyến tính (Uniform Affine Quantization):
$$q = \text{round}\left( \frac{x}{S} \right) + Z$$
Trong đó:
- **Scale ($S$):** Tỷ lệ co giãn thực:
  $$S = \frac{x_{max} - x_{min}}{q_{max} - q_{min}}$$
- **Zero-Point ($Z$):** Điểm không thực biểu diễn mức 0 thực tế trong không gian số nguyên:
  $$Z = \text{round}\left( -\frac{x_{min}}{S} \right) + q_{min}$$

### 7.2. Kết quả nén thực nghiệm của dự án
- Mô hình PyTorch FP32 gốc: **2.735,5 KB**
- Mô hình ONNX INT8 sau lượng tử hóa: **697,3 KB**
- **Tỷ lệ nén: 74,5%** (Hoàn thành xuất sắc chỉ tiêu kỹ thuật đề cương SIC là dưới 700 KB).
- **Độ chính xác suy giảm:** Chỉ rớt 0.67 điểm % (từ 94.33% xuống 93.66% trong phép thử end-to-end), nằm hoàn toàn trong dung sai an toàn 2% theo khuyến nghị y tế.

### 7.3. Giải thích hiện tượng độ trễ INT8 trên CPU thông thường
*Một câu hỏi phản biện rất hóc búa của chuyên gia phần cứng:*  
*"Tại sao trong benchmark CPU, ONNX FP32 chạy mất 0.29 ms mà bản INT8 lại mất 1.08 ms?"*

**Bản chất kiến trúc phần cứng máy tính:**
- Trên các bộ vi xử lý máy tính để bàn thông thường (CPU x86 không có phần cứng tăng tốc AI chuyên dụng), các phép tính ma trận không có bộ lệnh phần cứng xử lý trực tiếp số nguyên 8-bit (thiếu tập lệnh Intel Deep Learning Boost - VNNI).
- Do đó, thư viện runtime phải liên tục làm thao tác **Dequantize** từ INT8 lên FP32 để tính toán rồi lại **Quantize** ngược về INT8 để lưu trữ. Chi phí chuyển đổi (Type Casting Overhead) này làm tăng thời gian xử lý.
- **Tuy nhiên, giá trị cốt tử của INT8:**
  1. Giảm 74.5% dung lượng để nạp vừa bộ nhớ Flash ROM siêu nhỏ của chip IoT (vốn thường chỉ có $1 - 2\text{ MB}$ Flash).
  2. Khi được nạp lên các vi xử lý biên chuyên dụng (như Raspberry Pi 4/5, Jetson Nano, hoặc các chip ARM Cortex-M có nhân tăng tốc ARM NEON / Helium), phần cứng sẽ tính toán trực tiếp trên thanh ghi SIMD INT8, lúc đó INT8 sẽ nhanh hơn FP32 gấp 2 đến 4 lần và tiết kiệm hơn 60% điện năng tiêu thụ pin!

---

## 8. CƠ CHẾ SÀNG LỌC RUNG NHĨ (AFIB SCREENER)

### 8.1. Cơ chế bệnh học Rung nhĩ (Atrial Fibrillation)
Rung nhĩ là tình trạng tâm nhĩ phát xung điện hỗn loạn với tần số 350–600 lần/phút, làm nhĩ mất khả năng co bóp nhịp nhàng, máu ứ đọng tạo thành cục máu đông gây nhồi máu não đột quỵ.
- Trên điện tim, Rung nhĩ có 2 dấu hiệu kinh điển:
  1. Mất hoàn toàn sóng P bình thường, thay bằng các sóng lăn tăn (sóng f).
  2. Các khoảng cách giữa 2 đỉnh R liên tiếp ($RR$ intervals) biến thiên hoàn toàn ngẫu nhiên và hỗn loạn ("hoàn toàn không đều" - Irregularly Irregular).

### 8.2. Hệ thống đại lượng thống kê biến thiên nhịp tim (HRV)
Từ chuỗi khoảng cách nhịp $RR_1, RR_2, \dots, RR_N$:
1. Chuỗi hiệu khoảng cách liên tiếp: $\Delta RR_i = RR_{i+1} - RR_i$.
2. Hệ số biến thiên khoảng RR:
   $$CV_{RR} = \frac{\sigma_{RR}}{\mu_{RR}}$$
3. Chỉ số pNN50: Tỷ lệ phần trăm các khoảng cách nhịp liên tiếp có độ chênh lệch vượt quá $50\text{ ms}$:
   $$pNN50 = \frac{\text{Số lượng } |\Delta RR_i| > 50\text{ ms}}{\text{Tổng số khoảng } RR} \times 100\%$$

### 8.3. Shannon Entropy của phân phối $\Delta RR$
Shannon Entropy đo lường mức độ hỗn loạn thông tin của một quá trình ngẫu nhiên:
$$H(\Delta RR) = - \sum_{j=1}^{B} p_j \log_2(p_j)$$
Trong đó chuỗi $\Delta RR$ được chia thành $B$ khoảng giá trị (bins), $p_j$ là xác suất rơi vào khoảng $j$.
- Khi tim đập đều (nhịp xoang bình thường), các giá trị $\Delta RR$ tập trung hẹp quanh mức 0 $\rightarrow$ Entropy thấp ($H \rightarrow 0$).
- Khi bị Rung nhĩ, các giá trị $\Delta RR$ phân tán hỗn loạn khắp nơi $\rightarrow$ Entropy tăng vọt ($H > 0.62$).
- Hệ thống NEURO-ECG kết hợp Entropy, $CV_{RR}$ và $pNN50$ thành điểm số tổng hợp, kích hoạt cảnh báo nguy cấp khi vượt ngưỡng an toàn $0.62$.

---

## 9. HIỆN TƯỢNG DỊCH CHUYỂN MIỀN DỮ LIỆU (DOMAIN SHIFT)

### 9.1. Bản chất hiện tượng Domain Shift trong y tế
Một trong những điểm nghiên cứu khoa học được đánh giá cao nhất của nhóm là **thử nghiệm ngoại kiểm (External Validation)** trên các cơ sở dữ liệu hoàn toàn độc lập: SVDB, EDB và St. Petersburg INCART.
- **Hiện tượng quan sát:** Độ nhạy Recall của nhịp S (Ngoại tâm thu nhĩ) bị sụt giảm nặng nề khi kiểm tra trên nguồn ngoài (từ 81.29% trên test nội suy xuống còn dưới 5% trên SVDB).
- **Nguyên nhân cốt lõi (Root Cause):**
  1. **Khác biệt đạo trình dán điện cực (Lead Mismatch):** MIT-BIH dùng đạo trình Modified Limb Lead II (MLII) và V1; trong khi INCART và EDB dùng đạo trình 12 chuyển đạo tiêu chuẩn (Lead II, V5). Hình thái sóng P ở các đạo trình này có cực tính và biên độ khác hẳn nhau.
  2. **Khác biệt phần cứng thu nhận (Hardware Variability):** Bộ lọc phần cứng tương tự, độ phân giải ADC và tần số lấy mẫu gốc khác nhau tạo ra sự biến thiên đáp ứng pha.
  3. **Đặc thù quần thể bệnh nhân:** Mỗi bệnh viện thu nhận bệnh nhân ở các lứa tuổi, tiền sử bệnh và dùng các loại thuốc tim mạch khác nhau làm thay đổi hình dạng sóng.

### 9.2. Giải pháp kỹ thuật thích nghi miền (Domain Adaptation & Fine-tuning)
- Để chứng minh mô hình không bị "chết cứng", nhóm đã thực hiện thí nghiệm **Fine-tuning**: Đóng băng các tầng trích xuất đặc trưng phía dưới của ResNet-1D, mở khóa huấn luyện tầng phân loại cuối cùng trên một lượng nhỏ dữ liệu của tập INCART.
- **Kết quả:** Độ chính xác trên tập INCART lập tức tăng vọt từ **85.94% lên 93.18%**.
- Đây là cơ sở khoa học vững chắc để nhóm khẳng định với Hội đồng SIC: Hướng phát triển thương mại hóa tiếp theo sẽ là thu thập dữ liệu đa trung tâm và áp dụng mạng thích nghi miền đối kháng (Domain Adversarial Neural Networks - DANN).

---

## 10. HẠ TẦNG PHẦN MỀM Y TẾ, IEC 60601-1-8 & HUMAN-IN-THE-LOOP

### 10.1. Kiến trúc luồng dữ liệu thời gian thực (Event-Driven Streaming)
- Tín hiệu ECG phát ở tần số $360\text{ Hz}$ tạo ra khối lượng điểm dữ liệu lớn liên tục.
- Hệ thống chia nhỏ tín hiệu thành **36 gói tin mỗi giây** (mỗi gói chứa 10 mẫu liên tiếp) truyền phát qua giao thức **WebSocket bất đồng bộ** (FastAPI `websockets`).
- Tại Frontend, thư viện React 19 kết hợp đồ thị Plotly dựng khung hiển thị cửa sổ trượt (Sliding Window 1.000 điểm) đạt tần số quét **60 khung hình/giây (FPS)** mượt mà mà không làm đơ giao diện người dùng.

### 10.2. Mẫu thiết kế Singleton Pattern trong AI Service
- Nếu mỗi nhịp tim đến (mỗi 0.8 giây) lại khởi tạo một đối tượng mô hình nơ-ron hoặc cấp phát bộ nhớ tensor mới, hệ thống sẽ rơi vào tình trạng phân mảnh RAM và bộ dọn rác (Garbage Collector) của Python sẽ gây ra hiện tượng giật cục độ trễ (Latency Spikes).
- Dịch vụ `ECGInferenceService` được thiết kế theo mẫu **Singleton Pattern**: Nạp duy nhất 1 lần mô hình ResNet-1D và bộ Grad-CAM lên bộ nhớ RAM khi server khởi động. Mọi luồng suy luận dùng chung bộ đệm này, giữ độ trễ luôn ổn định dưới $0.3\text{ ms}$.

### 10.3. Tiêu chuẩn cảnh báo y tế quốc tế IEC 60601-1-8
Tiêu chuẩn quốc tế bắt buộc đối với tất cả máy theo dõi bệnh nhân trong phòng mổ và cấp cứu:
1. **Phân cấp 3 mức độ nguy hiểm:**
   - **Xanh (Low Priority):** Thông tin giám sát bình thường, nhịp xoang đều.
   - **Vàng (Medium Priority):** Nhịp tim nhanh ($>100\text{ BPM}$), nhịp chậm ($<60\text{ BPM}$) hoặc biến thiên nhẹ.
   - **Đỏ (High Priority / Alarm):** Nguy cơ tử vong trước mắt (Xuất hiện chuỗi nhịp Ngoại tâm thu thất PVC, Rung thất, hoặc Rung nhĩ ác tính). Đèn flash chớp đỏ, chuông cảnh báo âm thanh tần số cao vang lên liên tục.
2. **Cơ chế Tạm tắt chuông an toàn (Audio Alarm Pause):** Nút tắt âm tạm thời **120 giây** có đồng hồ đếm ngược trên màn hình, giúp kíp trực y tế có không gian xử trí ép tim hoặc sốc điện mà không bị ô nhiễm tiếng ồn hoảng loạn.

### 10.4. Cơ chế Human-in-the-loop & Bảng Audit Trail
- **Bác sĩ (Doctor/Admin)** có toàn quyền thẩm định lại kết luận của AI trên giao diện XAI.
- Nếu bác sĩ thấy AI nhận diện nhầm nhịp PVC thành N (hoặc ngược lại), bác sĩ bấm chọn nhãn đúng và nhấn "Xác nhận/Chỉnh sửa".
- Hệ thống tự động ghi một bản ghi bất biến vào bảng `audit_trails`:
  `{id, event_id, original_label, doctor_label, doctor_id, timestamp, note}`
- Bản ghi này đáp ứng 2 mục đích sống còn:
  1. **Tính toàn vẹn pháp lý y tế:** Xác định rõ ràng trách nhiệm chuyên môn của người ký duyệt.
  2. **Active Learning Data Pool:** Toàn bộ các nhịp bác sĩ sửa nhãn sẽ được gom lại làm dữ liệu quý giá để huấn luyện tinh chỉnh mô hình AI ở các phiên bản tiếp theo.

---

# BỘ BẢO BỐI TRẢ LỜI MỌI CÂU HỎI VẶN CỦA HỘI ĐỒNG (GRILLED DEFENSE CHEAT-SHEET)

### Câu 1: "Tại sao nhóm chọn ResNet-1D mà không dùng CNN-LSTM hay Transformer?"
> **Đáp:** "Dạ thưa Hội đồng, tín hiệu ECG từng nhịp có độ dài cục bộ 187 mẫu. Các bộ lọc tích chập cục bộ của ResNet-1D có tính chất bất biến tịnh tiến và độ nhạy rất cao với các điểm uốn sắc nhọn P-QRS-T. Cơ chế Skip Connection giải quyết triệt để vấn đề suy giảm đạo hàm, giúp ResNet-1D đạt F1-Macro 91.70% (vượt trội hoàn toàn so với CNN-LSTM 85.79% và Transformer 83.11%). Hơn nữa, ResNet-1D có độ trễ cực thấp chỉ 0.133 ms và cấu trúc tính toán ma trận thuần nhất, tối ưu tuyệt đối cho việc lượng tử hóa nén chip nhúng."

### Câu 2: "Tại sao Mamba-1D là mô hình rất mới mà kết quả lại thấp nhất?"
> **Đáp:** "Dạ thưa thầy cô, Mamba là State-Space Model tối ưu cho chuỗi dữ liệu cực kỳ dài (hàng nghìn đến chục nghìn tokens). Với một cửa sổ nhịp tim chỉ có 187 mẫu, cơ chế nhớ trạng thái nén của Mamba có xu hướng trơn hóa tín hiệu, vô tình làm mòn các gai nhọn cực ngắn của phức bộ QRS và sóng ngoại tâm thu, khiến mô hình bị mất chi tiết cục bộ so với các bộ lọc tích chập hẹp của ResNet."

### Câu 3: "Nhóm đã loại trừ hoàn toàn hiện tượng Data Leakage chưa?"
> **Đáp:** "Dạ nhóm đã phát hiện và loại trừ triệt để lỗi rò rỉ phổ biến trong cộng đồng nghiên cứu: tuyệt đối KHÔNG áp dụng SMOTE trước khi chia tập. Nhóm tách tập Stratified Validation 10% độc lập trước, sau đó chỉ áp dụng SMOTE trên nội bộ 90% tập Train. Minh chứng khoa học thực nghiệm là độ chính xác trên tập Validation đạt 98.62%, sát khít với tập Test là 98.51% (độ lệch chỉ 0.11%), chứng minh mô hình không hề overfit hay rò rỉ dữ liệu."

### Câu 4: "1D Grad-CAM có thực sự chứng minh được AI hiểu y khoa không?"
> **Đáp:** "Dạ Grad-CAM là bản đồ thuộc tính gradient nơ-ron (Neural Attribution Map). Kết quả thực nghiệm cho thấy trên nhịp Ngoại tâm thu thất PVC, bản đồ nhiệt tập trung hơn 85% năng lượng vào phức bộ QRS giãn rộng và sóng T đảo chiều; trên nhịp PAC tập trung vào sóng P đến sớm. Điều này chứng minh mạng nơ-ron đã thực sự kích hoạt dựa trên các cấu trúc giải phẫu sinh lý học tim mạch chứ không học vẹt các nhiễu nền ngẫu nhiên."

### Câu 5: "Lượng tử hóa ONNX INT8 có ý nghĩa thực tế gì khi chạy CPU chưa thấy nhanh hơn?"
> **Đáp:** "Dạ giá trị cốt tử của INT8 ở đây là nén 74.5% dung lượng từ 2.7 MB xuống 697.3 KB để nhúng vừa bộ nhớ Flash ROM của các vi điều khiển IoT đeo tay. Trên CPU thông thường thiếu tập lệnh VNNI nên mất chi phí ép kiểu casting; nhưng khi triển khai lên các chip biên chuyên dụng như Jetson Nano hoặc vi xử lý ARM có nhân NEON/Helium, INT8 sẽ bộc lộ toàn bộ ưu thế gia tốc phần cứng gấp 2–4 lần và tiết kiệm hơn 60% điện năng tiêu thụ."

### Câu 6: "Tại sao F1 trên tín hiệu WFDB thô lại giảm còn 61.80%?"
> **Đáp:** "Dạ vì phân phối mất cân bằng cực đoan trong tự nhiên: lớp Q chỉ có đúng 3 mẫu trong 20.546 nhịp tim và lớp F chỉ chiếm 0.74%. Chỉ số F1-Macro chia đều trọng số cho cả 5 lớp nên bị kéo giảm. Tuy nhiên, trên lớp loạn nhịp nguy cấp nhất là Ngoại tâm thu thất (PVC - Lớp V), hệ thống đạt độ nhạy Recall lên tới 97.30%, và thuật toán phát hiện đỉnh R Pan-Tompkins giữ vững độ chính xác F1 97.14%."

---
*Tài liệu này được biên soạn để phục vụ toàn diện cho buổi bảo vệ Capstone Project SIC 2026 của bạn Nguyễn Đào Nam Hải!*
