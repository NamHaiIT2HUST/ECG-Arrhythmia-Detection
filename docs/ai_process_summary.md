# Tổng Quan Quá Trình Xây Dựng AI (trước khi deploy)

Tài liệu này tổng hợp lại **toàn bộ quá trình liên quan đến AI/Machine Learning** của dự án —
từ dữ liệu, huấn luyện, benchmark kiến trúc, đến kiểm chứng độ chính xác, xuất mô hình nhẹ
(ONNX) và các module sàng lọc rối loạn nhịp bổ sung. **Không bao gồm** phần triển khai hạ tầng
(Docker, Nginx, Cloudflare Tunnel, CI/CD) — các phần đó xem [deployment_guide.md](deployment_guide.md).

Mục đích: có 1 nơi duy nhất trả lời "mô hình AI của chúng ta đã được xây dựng, kiểm chứng và
biết rõ giới hạn như thế nào" — dùng để viết báo cáo bảo vệ hoặc ôn lại khi cần.

---

## 1. Dữ liệu (Data)

Dự án dùng **2 nguồn dữ liệu** cho 2 mục đích khác nhau, xem chi tiết [dataset.md](dataset.md):

| Nguồn | Định dạng | Dùng để |
|---|---|---|
| **Kaggle MIT-BIH CSV** | Đã cắt sẵn từng nhịp, 187 điểm/nhịp | Huấn luyện & benchmark 5 kiến trúc model |
| **PhysioNet MIT-BIH gốc (WFDB)** | Tín hiệu thô liên tục 360Hz | Trích R-peak thật, kiểm chứng end-to-end, Grad-CAM, demo streaming real-time |

**Tiền xử lý** (`data/preprocess.py`, chi tiết [data_preprocessing.md](data_preprocessing.md)):
- Input: `mitbih_train.csv` (87.554 nhịp) + `mitbih_test.csv` (21.892 nhịp), 5 lớp AAMI
  (N/S/V/F/Q — Bình thường / Trên thất / Thất / Hợp nhất / Chưa phân loại).
- Dữ liệu gốc **mất cân bằng nặng** (lớp N chiếm >82%) → dùng **SMOTE** (sinh mẫu tổng hợp bằng
  nội suy K-Nearest Neighbors) để cân bằng **chỉ trên tập Train**, đưa cả 5 lớp về cùng số lượng
  (72.471 mẫu/lớp). Tập Test giữ nguyên phân phối thật, không SMOTE.
- **Bài học kỹ thuật quan trọng phát hiện sau này (xem mục 3)**: lúc đầu tách Validation *sau*
  SMOTE, gây rò rỉ dữ liệu (mẫu tổng hợp gần trùng lọt cả 2 tập) — đã sửa lại tách **trước** SMOTE.

---

## 2. Chọn kiến trúc model — Benchmark 5 kiến trúc 1D

Toàn bộ chi tiết: [benchmark_results.md](benchmark_results.md). Đã tự cài đặt và huấn luyện
**5 kiến trúc Deep Learning 1D** khác nhau trên cùng 1 tập dữ liệu, cùng 1 protocol Train/Test,
để chọn ra kiến trúc tốt nhất — không chỉ dùng 1 model có sẵn:

| Model | Accuracy | Precision | Recall | F1 (macro) | Latency | Tham số |
|---|---:|---:|---:|---:|---:|---:|
| **ResNet1D** ⭐ | **98.57%** | **92.49%** | 92.00% | **92.16%** | **0.13 ms** | 692.389 |
| CNN1D_LSTM | 97.27% | 81.26% | 93.58% | 85.79% | 0.18 ms | 242.885 |
| TCN | 96.17% | 76.94% | 94.69% | 82.81% | 0.79 ms | 171.365 |
| Transformer1D | 95.36% | 77.69% | 91.98% | 83.11% | 0.43 ms | 69.317 |
| Mamba1D | 94.45% | 74.27% | 87.92% | 79.28% | 0.47 ms | 59.877 |

**Chọn ResNet1D** vì accuracy/F1 cao nhất **và** latency thấp nhất trong 5 model — quan trọng
cho yêu cầu real-time. Kiến trúc: `Conv1d(k=7,s=2) → BN → ReLU → MaxPool` → 3× `ResNetBlock1D`
(Conv1d k=5 + BatchNorm + residual shortcut, kênh 32→64→128→256) → `AdaptiveAvgPool1d` →
`Linear(256, 5)`.

---

## 3. Sửa lỗi rò rỉ dữ liệu & huấn luyện lại có Validation đúng chuẩn

Đề cương yêu cầu chia rõ Train/Validation/Test. Lần thử đầu tách Validation **sau** SMOTE, phát
hiện Validation Accuracy bị thổi phồng giả tạo (99.78%) so với Test (98.56%) — nguyên nhân: mẫu
SMOTE tổng hợp trong Train gần trùng lọt sang Validation. **Sửa đúng gốc rễ**: tách Validation
(10%, stratified) **trước** khi chạy SMOTE, ngay trong `data/preprocess.py`.

**Kết quả sau khi sửa** (`saved_models/resnet1d.pth`):

| Tập | N mẫu | Accuracy |
|---|---:|---:|
| Train (đã SMOTE) | 326.115 | 99.94% |
| Validation (thật, trước SMOTE) | 8.756 | 98.62% |
| Test (thật) | 21.892 | 98.51% |

Val≈Test chỉ lệch **0.11 điểm %** — bằng chứng rõ ràng model **không overfit**, không còn rò rỉ
dữ liệu (khác hẳn 1.2 điểm % lệch ở lần tách sai trước đó). Val loss ổn định 0.070–0.078 từ
epoch 3, không phân kỳ.

**Kiểm chứng end-to-end trên dữ liệu PhysioNet thật** (`validate_classification.py`, tín hiệu
thô → lọc nhiễu → R-peak → model, so với nhãn bác sĩ thật trên 8 bản ghi, 20.546 nhịp):
**Accuracy 96.62%**, F1-macro 67.44% (thấp vì lớp Q gần như không có mẫu thật trong 8 bản ghi
này — đặc điểm vốn có của lớp hiếm nhất AAMI, không phải lỗi). Điểm đáng chú ý từ ma trận nhầm
lẫn: lớp **V (Thất/PVC — quan trọng lâm sàng nhất)** đạt recall 96.5%; lớp **F (Hợp nhất)** chỉ
đạt 56.1% do bản chất hình dạng lai giữa N và V, dễ nhầm kể cả với bác sĩ.

---

## 4. Phát hiện đỉnh R (QRS Detection) — Pan-Tompkins

`backend/core/qrs_detector.py` cài đặt thuật toán **Pan-Tompkins** để tìm đỉnh R động trên tín
hiệu thô (thay vì cắt cửa sổ cố định) — đây là bước bắt buộc trước khi đưa nhịp vào model, vì
mọi phép đo BPM/HRV/AFib sau này đều phụ thuộc trực tiếp vào độ chính xác của bước này.

**Kiểm chứng** (`backend/scripts/validate_qrs.py`, so với nhãn bác sĩ `.atr` thật trên 8 bản
ghi MIT-BIH): **F1 trung bình 97.14%**. Chi tiết theo từng bản ghi: 100→99.98%, 234→99.98%,
213→99.98%, 200→99.56%, 208→99.04%, 203→96.67%, 119→92.18%, 207→89.70%. Hai bản ghi thấp nhất
(207 — rung thất/cuồng nhĩ khiến hình dạng QRS gần như biến mất; 119 — PVC tần suất rất cao)
thuộc nhóm khó nhất toàn bộ MIT-BIH, kể cả với thuật toán thương mại.

**Bài học kỹ thuật quan trọng**: model được train trên dữ liệu Kaggle đã ở miền 125Hz + chuẩn
hoá biên độ [0,1] + cắt bắt đầu từ đỉnh R. Nếu đưa thẳng tín hiệu thô 360Hz vào model mà không
qua đúng pipeline này, tỷ lệ phát hiện bất thường tụt xuống còn 0.2% (đo thực tế lúc mới phát
hiện bug) — sau khi vá đủ 3 bước (lọc nhiễu, resample đúng cách toàn đoạn liên tục thay vì từng
nhịp lẻ, R-peak alignment), accuracy end-to-end mới đạt mức đáng tin cậy.

---

## 5. Explainable AI (XAI) — 1D Grad-CAM

`src/xai/gradcam1d.py`: khi model dự đoán 1 nhịp là bất thường (khác N), hệ thống chạy thêm
Grad-CAM 1D để tính heatmap — chỉ ra chính xác đoạn tín hiệu nào trong 187 điểm khiến model đưa
ra quyết định đó, thay vì chỉ trả về 1 nhãn "hộp đen". Heatmap này được gửi kèm qua WebSocket và
hiển thị trực tiếp trên biểu đồ ECG ở dashboard (dải đỏ chồng lên đúng đoạn sóng liên quan).

---

## 6. Rút gọn model cho triển khai nhẹ — ONNX Export & Quantization

Chi tiết: [onnx_comparison.md](onnx_comparison.md). Mục tiêu (CP6.1): thử xuất model sang định
dạng nhẹ hơn cho khả năng chạy trên thiết bị edge trong tương lai.

| Định dạng | Kích thước | Latency TB (CPU dev) | Accuracy end-to-end |
|---|---:|---:|---:|
| PyTorch FP32 (.pth) | 2735.5 KB | 1.14 ms | 94.33% (baseline) |
| ONNX FP32 | 2703.4 KB | 0.29 ms | 94.11% |
| ONNX INT8 quantized | **697.3 KB** | 1.09 ms | 93.66% |

**Kết luận nói thật**: mục tiêu kích thước (<700KB) đạt; độ chính xác đạt (rớt <2 điểm % so
baseline, trong ngưỡng chấp nhận); nhưng **INT8 không nhanh hơn trên CPU dev thông thường** —
đây là hạn chế đã biết của dynamic quantization (ONNX Runtime phải quantize/dequantize runtime
cho từng lớp), lợi ích tốc độ INT8 chỉ rõ trên phần cứng có tập lệnh tăng tốc chuyên dụng
(Intel AVX512-VNNI, NPU/GPU edge). Nếu chỉ cần tối ưu tốc độ mà không cần thu nhỏ file, **ONNX
FP32 là lựa chọn tốt hơn** trên phần cứng hiện tại.

---

## 7. Sàng lọc Rung nhĩ (AFib) & Nhịp nhanh — tầng rule-based riêng

Rung nhĩ là chẩn đoán theo **nhịp điệu kéo dài** (RR "irregularly irregular" + khả năng mất
sóng P) — khác bản chất với phân loại hình dạng từng nhịp đơn lẻ của ResNet1D, nên được tách
thành 1 tầng screening riêng, không gộp vào model 5 lớp AAMI:

- `backend/core/afib_screener.py` (`AfibScreener`): dùng real-time, tính điểm AFib tức thời từ
  cửa sổ trượt tối đa 50 khoảng RR gần nhất (độ không đều RR, pNN50, RMSSD).
- `backend/service/afib_screening_service.py`: dùng cho endpoint offline (upload file), phân
  tích toàn đoạn 1 lần, có thêm ước lượng vắng sóng P.

**Nợ kỹ thuật đã ghi nhận rõ, chưa giải quyết triệt để** (nói thật, không tô hồng):
- Ngưỡng `threshold = 0.62` hiện là **giá trị chọn tay theo trực giác**, chưa qua kiểm chứng
  thống kê đầy đủ. Đã thử hiệu chỉnh bằng dữ liệu AFDB thật (`calibrate_afib_thresholds.py`,
  đọc đúng nhãn nhịp điệu `.atr` thay vì giả định toàn bộ record là AFib), nhưng do môi trường
  làm việc bị giới hạn băng thông mạng nặng, chỉ tải được ~10 phút dữ liệu 1 bản ghi (04015) —
  không đủ để kết luận thống kê đáng tin (Youden's J ≈ 0 trên mẫu này). **Khuyến nghị**: coi
  cảnh báo AFib hiện tại là "gợi ý sàng lọc", không phải kết luận chẩn đoán, cho tới khi hiệu
  chỉnh lại với bộ AFDB đầy đủ.
- 2 công thức tính điểm giữa bản streaming và bản offline hiện chưa hợp nhất — có thể cho kết
  quả khác nhau trên cùng 1 tín hiệu tuỳ đi qua đường nào.

---

## 8. Kiểm chứng Generalization ngoài MIT-BIH

Câu hỏi quan trọng: model có học đúng đặc trưng sinh lý của rối loạn nhịp, hay chỉ học vẹt đặc
điểm riêng của 1 thiết bị/1 bệnh viện tạo ra MIT-BIH? Đã kiểm chứng trên **3 bộ dữ liệu
PhysioNet độc lập hoàn toàn khác** (khác bệnh viện, thiết bị, đạo trình, dân số bệnh nhân).

### 8.1. INCART (St Petersburg, Nga) — chạy thử trực tiếp, chưa fine-tune

| Record | Accuracy |
|---|---:|
| Tổng hợp 5 bản ghi (12.208 nhịp) | 85.94% |

Accuracy tụt ~11 điểm % so với 96.62% trên MIT-BIH — **domain shift thật**, không phải lỗi đo.
Chỉ số đáng tin hơn Accuracy (vì N chiếm 86.9% mẫu, baseline "đoán đại N" đã đạt 86.9%) là
**recall theo lớp**: N 86.1%, **V (PVC) 84.7%** — model vẫn giữ khả năng phát hiện nhịp thất
khá tốt trên dữ liệu hoàn toàn lạ. Đã loại trừ nguyên nhân "chọn sai đạo trình" (Lead I 84.57%
vs Lead II 85.94% — gần nhau). So sánh cả 5 kiến trúc trên cùng dữ liệu này: **ResNet1D vẫn
generalize tốt nhất** (85.94%), Mamba1D sụp đổ hẳn (46.50%, tệ hơn cả baseline ngây thơ).

### 8.2. Fine-tune trên INCART — đã thực hiện, đã đưa vào production

Mục tiêu: cải thiện INCART **mà không làm tụt** 4 chỉ tiêu đề cương trên MIT-BIH
(Accuracy/Precision/Recall/F1 ≥ 92/90/90/90%), không đổi kiến trúc. Dùng "replay fine-tuning":
train tiếp với LR thấp hơn 10-20 lần, trộn nhịp mới INCART với mẫu MIT-BIH gốc để chống quên.

3 lần thử, mỗi lần 1 bài học:

| Lần | Cấu hình | MIT-BIH Precision | MIT-BIH F1 | INCART Accuracy | Đạt 4/4 mục tiêu? |
|---|---|---:|---:|---:|:---:|
| 0 (gốc) | — | 92.63% | 92.16% | 85.94% | ✅ |
| 1 | giữ cả lớp S | 87.30% | 89.45% | 92.40% | ❌ |
| 2 | giảm liều lượng | 88.63% | 90.24% | 90.23% | ❌ |
| **3** | **loại lớp S khỏi fine-tune** | **91.48%** | **91.70%** | **93.18%** | **✅** |

**Nguyên nhân gốc rễ tìm ra**: lớp S (Trên thất) của INCART có hình dạng khác đủ nhiều so với
MIT-BIH khiến việc trộn lẫn làm lệch hẳn ranh giới quyết định lớp này, dù chỉ chiếm 6.5% dữ
liệu fine-tune. Giải pháp đúng: loại có chọn lọc theo từng lớp, không phải giảm đều cường độ
train (giảm epoch/LR không giải quyết được gốc rễ). **Bản fine-tune lần 3 đã được promote lên
production** (`saved_models/resnet1d.pth` hiện tại) — bản gốc backup local, không commit git.

Kết quả cuối trên MIT-BIH Test (trước→sau fine-tune): N 99.2%→99.2%, S 83.9%→83.9% (không đổi,
đúng thiết kế), V 96.0%→95.6%, F 82.5%→80.7% (tụt nhẹ), Q 99.2%→99.1%. INCART held-out:
85.94%→**93.18%** (+7.24 điểm %), Recall N 86.1%→93.9%, Recall V 84.7%→88.6%.

### 8.3. SVDB & EDB — kiểm chứng thêm 2 bộ độc lập nữa (không train)

| Dataset | Accuracy | Recall N | Recall S | Recall V | Recall F |
|---|---:|---:|---:|---:|---:|
| MIT-BIH Test (tham chiếu) | 98.43% | 99.2% | 81.3% | 96.2% | 84.0% |
| INCART (đã fine-tune riêng) | 93.18% | 93.9% | — | 88.6% | — |
| SVDB | 77.32% | 95.1% | **0.4%** | 78.2% | — |
| EDB | 76.85% | 78.1% | **3.6%** | 92.2% | **2.3%** |

**Tin tốt**: lớp N và V (2 lớp quan trọng nhất lâm sàng) generalize nhất quán trên cả 4 bộ dữ
liệu độc lập (V dao động 78-96%, không sụp đổ ở bộ nào). **Tin cần nói thẳng**: lớp S sụp đổ gần
như hoàn toàn trên cả 2 bộ mới (0.4%, 3.6%) — cùng nguyên nhân gốc đã phát hiện lúc fine-tune
INCART: ranh giới quyết định lớp S học "quá khít" theo đặc điểm riêng của MIT-BIH.

### 8.4. Hai lần thử sửa lớp S bằng SVDB — đều thất bại (ghi nhận trung thực)

Thử fine-tune tiếp bằng dữ liệu SVDB (giàu nhịp S nhất hiện có) theo 2 kỹ thuật khác nhau:

- **Fine-tune toàn mạng**: Recall_S cải thiện thật (0.4%→25.7%, transfer cả sang EDB
  3.6%→26.7%) nhưng **lớp V sụp đổ trên diện rộng** (INCART Recall_V 88.6%→51.2%, EDB
  92.2%→67.7%).
- **Linear probing** (chỉ train lớp cuối, đóng băng backbone): gây hại nhẹ hơn nhưng S cải
  thiện cũng kém hẳn (cao nhất 1.5%) và V vẫn bị ảnh hưởng rõ.

**Kết luận khoa học (giá trị hơn cả việc "sửa được hay không")**: 2 kỹ thuật khác nhau đều thất
bại theo cùng 1 kiểu — cải thiện S luôn đi kèm cái giá làm hại V. Đây là bằng chứng vấn đề nằm ở
**bản chất hình học của bài toán phân loại 5 lớp dùng chung 1 mặt quyết định (softmax)**: đặc
trưng nhịp SVDB nằm ở vùng mơ hồ giữa các lớp trong không gian đã học từ MIT-BIH — kéo về đúng
lớp S tất yếu kéo theo xáo trộn lớp lân cận V. Cách sửa triệt để duy nhất là **train lại từ đầu**
với dữ liệu MIT-BIH + SVDB + INCART trộn sẵn từ vòng chia Train/Val/Test đầu tiên — khối lượng
tương đương làm lại toàn bộ pipeline training, **đã được quyết định chủ động KHÔNG làm** ở đợt
này. Production giữ nguyên bản fine-tune INCART (lần 3).

---

## 9. Tóm tắt giới hạn đã biết (để không hứa quá tay khi bảo vệ)

- **Phạm vi triển khai an toàn**: thiết bị đo cùng chuẩn đạo trình Holter/MLII tương tự MIT-BIH
  (đúng như hệ thống hiện tại đang giả lập). Đổi sang thiết bị/đạo trình khác hẳn, cần fine-tune
  lại trước khi triển khai.
- **Lớp N và V generalize tốt** trên mọi bộ dữ liệu độc lập đã thử (78-96% recall V).
- **Lớp S và F cần dữ liệu huấn luyện đa nguồn ngay từ đầu** mới generalize tốt ra ngoài MIT-BIH
  — không phải thiếu sót của lần triển khai này, mà là hướng phát triển tiếp theo hợp lý.
- **Ngưỡng AFib (0.62) chưa được kiểm chứng thống kê đầy đủ** — nên coi là gợi ý sàng lọc, không
  phải kết luận chẩn đoán, cho đến khi hiệu chỉnh lại với bộ AFDB đầy đủ.
- **File ONNX hiện đã đồng bộ với trọng số fine-tune mới nhất** (xuất lại sau lần fine-tune INCART
  để tránh dùng nhầm trọng số cũ).

---

## 10. Cách tái tạo / kiểm thử lại toàn bộ pipeline AI

```bash
python data/preprocess.py                                  # tiền xử lý + SMOTE + tách Val/Test đúng cách
python src/benchmark.py                                     # train & benchmark cả 5 kiến trúc
python -m backend.scripts.validate_qrs                      # F1 phát hiện đỉnh R so nhãn bác sĩ
python -m backend.scripts.validate_classification            # accuracy end-to-end (raw signal -> AAMI)
python -m backend.scripts.plot_c2_diagnostics                 # biểu đồ kiểm chứng Val/Test + confusion matrix
python -m src.models.export_onnx                             # xuất ONNX FP32 + INT8
python -m backend.scripts.validate_onnx_classification        # so sánh accuracy PyTorch vs ONNX
python -m backend.scripts.download_external_incart            # tải INCART
python -m backend.scripts.validate_external_incart             # kiểm chứng generalization INCART
python -m backend.scripts.compare_models_incart                # so sánh cả 5 kiến trúc trên INCART
python -m backend.scripts.finetune_resnet1d_incart              # fine-tune (loại lớp S)
python -m backend.scripts.validate_external_db --data-dir <dir> --channel <n> --records <ids> --name <tên>  # SVDB/EDB
python -m backend.scripts.download_afdb_sample                  # tải mẫu AFDB
python -m backend.scripts.calibrate_afib_thresholds              # hiệu chỉnh ngưỡng AFib bằng nhãn thật
```
