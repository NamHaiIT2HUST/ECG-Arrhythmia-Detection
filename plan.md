# KẾ HOẠCH PHÁT TRIỂN HỆ THỐNG ECG ARRHYTHMIA DETECTION & EXPLAINABLE AI (XAI)
> **Tài liệu Kế hoạch Chi tiết & Phân bổ Checkpoint Toàn diện**
> **Dự án**: Giám sát điện tâm đồ (ECG) thời gian thực & Phát hiện rối loạn nhịp tim ứng dụng Học sâu & XAI
> **Cập nhật lần cuối**: 2026-08-30
> **Trạng thái Codebase hiện tại**: Checkpoint 1-3 hoàn thành (Data, 5 Models Benchmark, 1D Grad-CAM, FastAPI WebSocket + DSP/R-peak/HRV backend, React Plotly UI V3). Checkpoint 4-6 chưa bắt đầu.
> **Phân công công việc cho 2 người từ đây trở đi**: xem [pccv.md](pccv.md).

---

## I. TỔNG QUAN HIỆN TRẠNG TOÀN BỘ CÁC NHÁNH (GIT AUDIT)

| Tên nhánh (Branch) | Trạng thái | Nội dung đã hoàn thành | Đánh giá & Vấn đề tồn đọng |
|:---|:---:|:---|:---|
| `main` | ✅ Chuẩn | Đã fast-forward merge toàn bộ `feat/frontend-integration` (data, AI models, XAI, backend, websocket, frontend) + vá lỗi tiền xử lý real-time (2026-08-29). | Là nhánh nền cho mọi nhánh mới từ giờ. |
| `feat/dsp-and-beat-segmentation` | ✅ Hoàn thành, đã merge vào `main` | Toàn bộ Checkpoint 3 (backend): DSP filter, Pan-Tompkins R-peak, BPM/HRV, record switcher API, upload diagnosis API. | Frontend CHƯA nối với các API này — xem CP 3.6 và [pccv.md](pccv.md). |
| `feat/data`, `feat/ai-model-development`, `feat/explainable-ai`, `feat/websocket`, `feat/backend-integration`, `frontend`, `backend` | Hoàn thành, đã merge vào `main` | Đã là ancestor của `main`, không còn công việc riêng. | Có thể xoá các nhánh remote đã merge nếu muốn dọn repo (không bắt buộc). |

---

## II. LỘ TRÌNH VÀ CÁC CHECKPOINT LỚN (MAJOR CHECKPOINTS)

```mermaid
flowchart TD
    CP1["<b>Checkpoint 1 (HOÀN THÀNH)</b><br/>Dữ liệu & Mô hình AI Cốt lõi & XAI"]
    CP2["<b>Checkpoint 2 (HOÀN THÀNH)</b><br/>Hạ tầng Real-time WebSocket & Dashboard MVP"]
    CP3["<b>Checkpoint 3 (HOÀN THÀNH — backend)</b><br/>Xử lý Tín hiệu Số (DSP) & Phân đoạn Nhịp Động"]
    CP4["<b>Checkpoint 4 (TIẾP THEO)</b><br/>Nghiệp vụ Y tế Lâm sàng & Báo cáo Thông minh (AI Report)"]
    CP5["<b>Checkpoint 5</b><br/>Cơ sở Dữ liệu, Xác thực & Phân quyền (Auth & Database)"]
    CP6["<b>Checkpoint 6</b><br/>Tối ưu Edge AI, Đóng gói Docker & Kiểm thử Toàn diện"]

    CP1 --> CP2
    CP2 --> CP3
    CP3 --> CP4
    CP3 -.CP3.6 nối FE, có thể làm song song CP4/CP5.-> CP4
    CP4 --> CP5
    CP4 -.có thể làm song song với CP5.-> CP5
    CP5 --> CP6
```

> Từ Checkpoint 4 trở đi, công việc **được chia cho 2 người làm song song** theo 2 track gần như độc lập (Frontend/Lâm sàng vs Backend/Hạ tầng). Chi tiết phân công, thứ tự làm, và các điểm cần đồng bộ giữa 2 người: xem [pccv.md](pccv.md). Tài liệu này (`plan.md`) là nguồn kỹ thuật chi tiết (specs) cho từng checkpoint; `pccv.md` là bảng phân công + giao tiếp.

---

## III. CHI TIẾT TỪNG CHECKPOINT VÀ SUB-CHECKPOINTS

---

### 🟢 CHECKPOINT 1: DỮ LIỆU, MÔ HÌNH HỌC SÂU (AI CORE) & EXPLAINABLE AI
> **Trọng tâm**: Xây dựng nền tảng học máy vững chắc, giải quyết triệt để vấn đề mất cân bằng dữ liệu và tính minh bạch của mô hình AI.
> **Trạng thái**: ✅ 100% hoàn thành. **Không cần làm gì thêm ở checkpoint này** (xem mục 3.0 ở Checkpoint 3 — đã xác nhận model đủ tốt, không cần train lại).

#### 1.1. Nguồn dữ liệu (`data/`)
- **Kaggle CSV** (`data/raw/kaggle_csv/mitbih_train.csv`, `mitbih_test.csv`): bộ "ECG Heartbeat Categorization Dataset" — tín hiệu MIT-BIH đã được cộng đồng tiền xử lý sẵn: **resample về 125Hz**, mỗi nhịp cắt bắt đầu từ đỉnh R, độ dài động theo RR (~1.2× RR), **đệm số 0 (zero-pad)** cho đủ 187 điểm, **chuẩn hoá biên độ min-max về [0, 1]**. Đây chính là bộ dữ liệu dùng để **train 5 model** (xem `src/benchmark.py::load_data("kaggle")`).
  - `mitbih_train.csv`: 87.554 mẫu nhịp tim. `mitbih_test.csv`: 21.892 mẫu.
- **PhysioNet WFDB gốc** (`data/raw/physionet_mitdb/*.dat/.hea/.atr`): 48 bản ghi tín hiệu ECG thô liên tục ở **360Hz**, biên độ mV thực (vd record 208: khoảng -3.5 đến 3.65mV), kèm nhãn đỉnh R + loại nhịp do bác sĩ đánh (`.atr`, đọc bằng `wfdb.rdann`). Dùng để: (a) mô phỏng luồng real-time trong `backend/service/data_streamer.py`, (b) làm ground-truth kiểm chứng toàn bộ pipeline CP3 (`backend/scripts/validate_qrs.py`, `validate_classification.py`).
- **Phân loại chuẩn 5 lớp AAMI** (dùng xuyên suốt toàn bộ hệ thống, xem `data/preprocess.py::AAMI_CLASSES`):
  | Lớp | Tên | Ký hiệu MIT-BIH gộp vào |
  |:---:|:---|:---|
  | 0 - N | Normal beat (Bình thường) | N, L, R, e, j |
  | 1 - S | Supraventricular ectopic (Trên thất) | A, a, J, S |
  | 2 - V | Ventricular ectopic / PVC (Thất) | V, E |
  | 3 - F | Fusion beat (Hợp nhất) | F |
  | 4 - Q | Unknown/Unclassifiable (Chưa rõ) | /, f, Q |

#### 1.2. Tiền xử lý & cân bằng dữ liệu (`data/preprocess.py`)
- Đọc CSV/WFDB → tách X (tín hiệu 187 điểm) / y (nhãn).
- Với nhánh PhysioNet: lọc Butterworth bandpass 0.5-40Hz (`butter_bandpass_filter`), cắt cửa sổ ±93 mẫu quanh mỗi đỉnh R đã gán nhãn, chia train/test 80/20 stratified (`random_state=42`) **trước khi** áp SMOTE (tránh rò rỉ dữ liệu test).
- **SMOTE** (Synthetic Minority Over-sampling): áp trên tập train của cả 2 nguồn, cân bằng về **72.471 mẫu/lớp** (Kaggle). Tập test giữ nguyên phân phối thật (không SMOTE) để đánh giá trung thực.
- Output: `data/processed/X_train_kaggle.npy`, `y_train_kaggle.npy`, `X_test_kaggle.npy`, `y_test_kaggle.npy` (và tương tự `_physio` nếu chạy nhánh PhysioNet). Các file `.npy` này **không commit vào git** (`.gitignore`), phải tự chạy `python data/preprocess.py` để tái tạo.

#### 1.3. Kiến trúc & benchmark 5 model (`src/models/`, `src/benchmark.py`)
Huấn luyện với `BATCH_SIZE=128`, `EPOCHS=10`, `Adam lr=1e-3`, `CrossEntropyLoss`, trên `data/processed/*_kaggle.npy`. Kết quả đầy đủ tại [docs/benchmark_results.md](docs/benchmark_results.md):

| Model | File | Accuracy | Precision | Recall | F1 (macro) | Latency | Params |
|:---|:---|---:|---:|---:|---:|---:|---:|
| **ResNet1D** ⭐ production | `src/models/resnet1d.py` | **98.57%** | 92.49% | 92.00% | **92.16%** | **0.13ms** | 692.389 |
| CNN1D_LSTM | `src/models/cnn_lstm.py` | 97.27% | 81.26% | 93.58% | 85.79% | 0.18ms | 242.885 |
| TCN | `src/models/tcn.py` | 96.17% | 76.94% | 94.69% | 82.81% | 0.79ms | 171.365 |
| Transformer1D | `src/models/transformer1d.py` | 95.36% | 77.69% | 91.98% | 83.11% | 0.43ms | 69.317 |
| Mamba1D | `src/models/mamba1d.py` | 94.45% | 74.27% | 87.92% | 79.28% | 0.47ms | 59.877 |

- **Vì sao chọn ResNet1D**: accuracy/F1 cao nhất VÀ latency thấp nhất trong 5 model (0.13ms/nhịp, quan trọng cho real-time). Kiến trúc: `prep` (Conv1d k=7,s=2 → BN → ReLU → MaxPool) → 3× `ResNetBlock1D` (Conv1d k=5 + BN + residual shortcut, kênh 32→64→128→256) → `AdaptiveAvgPool1d` → `Linear(256, 5)`.
- Trọng số đã train lưu tại `saved_models/*.pth` (**không commit git**, ~2.7MB mỗi file — xem README mục "Dữ liệu & trọng số model" để tái tạo bằng `python src/benchmark.py`).
- **Kiểm chứng lại 2026-08-30** (CP3.3, `backend/scripts/validate_classification.py`): chạy nguyên trọng số ResNet1D này (không train lại) qua pipeline serving đã sửa đúng (lọc + Pan-Tompkins + resample 125Hz + pad/truncate) trên tín hiệu THẬT (raw PhysioNet, không phải test set đã tiền xử lý sẵn) → **Accuracy 94.33%** trên 20.546 nhịp / 8 bản ghi, khớp hợp lý với benchmark offline. Kết luận: **model KHÔNG cần train lại**, chênh lệch ~4% so với benchmark offline đến từ (a) R-peak detector không hoàn hảo 100% (F1 97.14%) và (b) tái tạo phương pháp windowing của Kaggle chỉ là gần đúng tốt nhất có thể (không có tài liệu chính thức mô tả chính xác thuật toán gốc).

#### 1.4. Explainable AI — 1D Grad-CAM (`src/xai/gradcam1d.py`)
- `GradCAM1D`: hook vào `model.layer3` (block cuối ResNet1D) để lấy activation + gradient, tính trọng số `alpha = mean(gradient)`, `cam = ReLU(sum(alpha * activation))`, nội suy tuyến tính (`F.interpolate`) về đúng 187 điểm, chuẩn hoá [0,1].
- `Saliency1D`: phương án phụ (gradient × input), nhanh hơn nhưng ít trực quan hơn — hiện chưa được dùng trong luồng chính, để sẵn cho ai muốn so sánh phương pháp XAI khác.
- Chỉ chạy khi model dự đoán bất thường (`pred_class > 0`) để tiết kiệm tài nguyên (backward pass tốn hơn forward pass).
- Test độc lập: `src/xai/test_xai.py`.

#### 1.5. Sub-checkpoints
- [x] **CP 1.1** Data Ingestion & Formatting
- [x] **CP 1.2** Imbalanced Data Handling (SMOTE)
- [x] **CP 1.3** Deep Learning Suite Construction (5 kiến trúc)
- [x] **CP 1.4** Model Benchmarking & Selection
- [x] **CP 1.5** Explainable AI (1D Grad-CAM)

---

### 🟢 CHECKPOINT 2: HẠ TẦNG WEBSOCKET REAL-TIME & GIAO DIỆN MONITORING MVP
> **Trọng tâm**: Kết nối luồng dữ liệu liên tục từ Backend sang Frontend với độ trễ tối thiểu và trực quan hóa nhịp tim thời gian thực.
> **Trạng thái**: ✅ 100% hoàn thành (đã được nâng cấp thêm ở Checkpoint 3, xem payload mới ở mục 3.4).

#### 2.1. Kiến trúc Backend (`backend/`)
```
backend/
├── main.py              # FastAPI app, lifespan (load model lúc startup), CORS, mount router
├── core/
│   ├── config.py         # Settings (pydantic-settings): CORS origins, project name
│   ├── signal_processing.py   # (CP3) bandpass_filter, notch_filter, normalize_window
│   ├── qrs_detector.py        # (CP3) Pan-Tompkins, extract_beat_window, resample_signal
│   └── hrv.py                 # (CP3) HRVTracker, compute_bpm/sdnn/rmssd
├── api/
│   ├── ws_routes.py       # WS /ws/ecg (stream real-time)
│   ├── records_routes.py  # (CP3) GET /api/records
│   └── diagnosis_routes.py# (CP3) POST /api/diagnosis/upload-ecg
├── service/
│   ├── inference_service.py  # Singleton ECGInferenceService (load model, predict + Grad-CAM)
│   ├── data_streamer.py      # ecg_file_reader() - đọc file WFDB, lọc, phát hiện đỉnh R, stream
│   └── diagnosis_service.py  # (CP3) run_offline_diagnosis, parse_ecg_csv
└── scripts/               # Script tiện ích + kiểm thử thủ công (không phải pytest)
```

#### 2.2. WebSocket streaming
- Endpoint `WS /ws/ecg?record=<id>` (query param `record` được thêm ở CP3.4, mặc định `208`).
- `ecg_file_reader()`: đọc toàn bộ 1 bản ghi WFDB, gửi từng gói **10 điểm / 1/36 giây** (= 360 điểm/giây, đúng chuẩn tần số MIT-BIH), lặp lại từ đầu khi hết file (demo chạy vô hạn).
- `ECGInferenceService` (singleton, nạp model 1 lần lúc `lifespan` startup trong `main.py`): `predict(beat_window)` → `(label, heatmap|None, latency_ms)`.

#### 2.3. Payload WebSocket (schema hiện tại, sau CP3 — xem thêm mục 3.4)
```jsonc
{
  "chunk": [10 float],        // điểm tín hiệu mới để vẽ tiếp biểu đồ (đã lọc nhiễu)
  "prediction": "BÌNH THƯỜNG" | "CẢNH BÁO: ...",  // giữ nguyên giữa 2 nhịp (sample-and-hold)
  "heatmap": [187 float] | null,  // CHỈ khác null đúng ở gói tin vừa chẩn đoán 1 nhịp mới
  "latency_ms": float,
  "confidence": float,         // xác suất softmax của nhãn dự đoán gần nhất (0-1), thêm ở CP5.3
  "bpm": float,
  "hrv_sdnn": float,
  "hrv_rmssd": float,
  "is_new_beat": boolean       // true đúng lúc vừa có 1 nhịp mới được chẩn đoán
}
```

#### 2.4. Kiến trúc Frontend (`frontend/src/`)
```
frontend/src/
├── App.jsx                 # Tab routing (dashboard/patient/xai/settings), state activeTab
├── main.jsx
├── context/
│   └── AnomalyContext.jsx  # Lưu lịch sử tối đa 20 nhịp lỗi gần nhất (in-memory, mất khi F5)
├── pages/
│   ├── DashboardPage.jsx   # Kết nối WS, quản lý xData/yData/heatmap, auto-reconnect 3s
│   └── XAIPage.jsx         # Danh sách lịch sử cảnh báo + Plotly Bar+Line kết hợp (heatmap đè lên sóng ECG)
├── components/
│   ├── layout/Header.jsx, Sidebar.jsx   # 4 tab: Theo Dõi Trực Tuyến, Hồ Sơ Bệnh Nhân*, Phân Tích XAI, Cài Đặt*
│   └── dashboard/ECGChart.jsx, StatCards.jsx, EventLog.jsx, PatientInfo.jsx, LoadingSpinner.jsx
└── api/axios.js            # (hiện chưa dùng nhiều — CP3 dùng fetch/axios trực tiếp cho REST mới)
```
`*` = tab hiện là **placeholder tĩnh** trong `App.jsx` (dòng "tính năng đang được phát triển") — chính là phạm vi Checkpoint 4.

#### 2.5. Sub-checkpoints
- [x] **CP 2.1** FastAPI WebSocket Engine (router, lifespan, connect/disconnect)
- [x] **CP 2.2** Simulated Streamer Service (đọc file PhysioNet)
- [x] **CP 2.3** Real-time Inference Pipeline (buffer → predict → JSON payload)
- [x] **CP 2.4** React Plotly Streaming Dashboard (1000 điểm gần nhất, StatCards)
- [x] **CP 2.5** Anomaly Context & XAI Inspector (lưu + xem lại heatmap)

---

### 🟢 CHECKPOINT 3: XỬ LÝ TÍN HIỆU SỐ (DSP) NÂNG CAO & CẮT PHỨC BỘ R-PEAK ĐỘNG
> **Trọng tâm**: Chuyển từ việc cắt cửa sổ tĩnh 187 điểm sang xử lý tín hiệu thực tế: lọc nhiễu y tế và tự động nhận diện đỉnh R (Pan-Tompkins), tính BPM/HRV thật, cho phép chọn bản ghi và chẩn đoán offline từ file upload.
> **Trạng thái**: ✅ 100% hoàn thành ở backend (2026-08-30, nhánh `feat/dsp-and-beat-segmentation` đã merge `main`). ⚠️ Frontend CHƯA nối (CP 3.6, xem [pccv.md](pccv.md)).

#### 3.0. 🔴 CHẨN ĐOÁN GỐC RỄ: Vì sao kết quả real-time từng có vẻ "kém" dù benchmark cao?
**Không cần train lại 5 model.** Benchmark (`docs/benchmark_results.md`) hợp lệ, không data leakage. ResNet1D 98.57% Acc / 92.16% F1-macro là số thật.

**Lỗi thật nằm ở tầng serving (real-time inference pipeline), không phải ở model:**
- Model train trên Kaggle MIT-BIH Heartbeat CSV: tín hiệu **125Hz**, cắt theo nhịp (bắt đầu từ đỉnh R), **chuẩn hoá biên độ [0,1]**.
- `data_streamer.py` (bản cũ) đọc tín hiệu **thô** từ PhysioNet `.dat` (**360Hz**, biên độ mV thật, vd record 208: -3.5 đến 3.65) và đưa thẳng sliding-window 187 điểm thô vào model — lệch hoàn toàn miền dữ liệu train (sai cả biên độ lẫn thời lượng cửa sổ).
- Bằng chứng đo được (2026-08-29): quét 10.000 điểm đầu record 208 — **trước khi vá: chỉ phát hiện 0.2%** bất thường. Sau khi thêm lọc + chuẩn hoá biên độ (`signal_processing.py`, chưa có R-peak alignment): **22.9%**.
- Sau khi hoàn thiện CP3.2/3.3 (R-peak alignment + đúng miền 125Hz + pad/truncate đúng cách — xem mục 3.2 bên dưới): **kiểm chứng end-to-end trên nhãn bác sĩ đạt Accuracy 94.33%**. Đây là con số cuối cùng, đáng tin cậy.

#### 3.1. Bài học kỹ thuật quan trọng nhất của Checkpoint 3 (đọc trước khi động vào pipeline AI)
Lần thử đầu tiên của CP3.2 dùng `scipy.signal.resample()` để co giãn (time-warp) **từng nhịp riêng lẻ** về đúng 187 điểm sau khi cắt theo đỉnh R — nghe rất hợp lý (và là cách nhiều tutorial online mô tả). Nhưng **kiểm tra trực tiếp** `data/processed/X_train_kaggle.npy` cho thấy mọi nhịp trong bộ dữ liệu train **có đuôi toàn số 0** — tức là bộ dữ liệu gốc được tạo bằng cách **cắt nhịp có độ dài động (~1.2× RR) rồi ĐỆM SỐ 0 (zero-pad)/CẮT BỚT cho đủ 187 điểm ở 125Hz, KHÔNG hề co giãn (resample) hình dạng từng nhịp**. Resample từng nhịp làm méo hình dạng QRS thật so với những gì model đã học, khiến Accuracy chẩn đoán rơi từ ~92% (benchmark) xuống còn **~27%** dù R-peak detection vẫn đúng gần như hoàn hảo. Đây là lỗi rất dễ mắc lại nếu ai đó "tối ưu lại" phần cắt nhịp trong tương lai — **luôn kiểm tra bằng `validate_classification.py` sau bất kỳ thay đổi nào ở `qrs_detector.py`**, đừng chỉ tin vào lý thuyết.

Quy tắc đúng đã áp dụng: **resample được phép áp dụng cho TOÀN BỘ đoạn tín hiệu liên tục** (360Hz → 125Hz, 1 lần cho cả bản ghi — đây là chuyển đổi tần số lấy mẫu hợp lệ, không làm méo hình dạng tương đối giữa các nhịp), nhưng **KHÔNG được áp dụng cho từng nhịp đã cắt riêng lẻ** (phải pad/truncate).

#### 3.2. Module DSP & R-Peak Detection (`backend/core/signal_processing.py`, `backend/core/qrs_detector.py`)

**`signal_processing.py`**:
- `bandpass_filter(signal, lowcut=0.5, highcut=45.0, fs=360, order=4)`: Butterworth + `filtfilt` (zero-phase), loại trôi đường nền + nhiễu tần số cao.
- `notch_filter(signal, cutoff=50.0, q=30.0, fs=360)`: `iirnotch` + `filtfilt`, khử nhiễu điện lưới.
- `normalize_window(window)`: min-max về [0,1], trả `np.zeros` nếu tín hiệu phẳng (tránh chia 0).

**`qrs_detector.py`** — 3 hàm chính:
1. `pan_tompkins_r_peaks(signal, fs=360)`: bandpass 5-15Hz (nhấn phổ QRS) → đạo hàm → bình phương → tích phân cửa sổ trượt ~150ms → `find_peaks` với ngưỡng thích nghi (`0.35 × mean`) + khoảng cách tối thiểu 200ms → hiệu chỉnh lại vị trí đỉnh trên tín hiệu GỐC trong bán kính **±120ms** (không phải ±40ms sách giáo khoa — QRS giãn rộng của nhịp Thất/Fusion khiến "bướu" năng lượng trên tín hiệu tích phân lệch xa đỉnh R thật ~28-33 mẫu, phải nới bán kính tìm kiếm mới bắt kịp).
   - **Kiểm chứng** (`backend/scripts/validate_qrs.py`, so nhãn bác sĩ `.atr`, 8 bản ghi): **F1 trung bình 97.14%** (100→99.98%, 234→99.98%, 213→99.98%, 200→99.56%, 208→99.04%, 203→96.67%, 119→92.18%, 207→89.70% — 2 bản ghi thấp nhất là 207 (rung thất/cuồng nhĩ, hình dạng QRS gần như biến mất) và 119 (PVC tần suất rất cao), đây là 2 trong số các bản ghi khó nhất toàn bộ MIT-BIH kể cả với thuật toán thương mại).
2. `resample_signal(signal, orig_fs, target_fs)`: resample **toàn đoạn tín hiệu liên tục** (dùng 1 lần/bản ghi, 360→125Hz).
3. `extract_beat_window(signal, r_peaks, index, window_size=187, fs=125)`: cắt từ đỉnh R, độ dài = `min(max(1.2×RR_kế_tiếp, 200ms), ...)`, rồi **pad số 0/cắt bớt** — không resample (xem mục 3.1). `compute_all_beats(signal, fs=360, model_fs=125)`: tiện ích chạy cả 3 bước trên cho 1 bản ghi, dùng trong `diagnosis_service.py` và các script validate; **trả chỉ số đỉnh R theo trục thời gian GỐC** (360Hz) để còn khớp với vị trí thực trong luồng stream.
   - `MODEL_FS = 125` là hằng số dùng chung, định nghĩa ngay trong `qrs_detector.py`.

**`hrv.py`**:
- `HRVTracker(fs, max_history=50)`: theo dõi lịch sử khoảng RR gần nhất (tối đa 50 nhịp), `update(r_peak_idx)` trả `{bpm, hrv_sdnn, hrv_rmssd}`. Mỗi kết nối WebSocket có 1 instance riêng (không dùng chung state toàn cục — tránh lỗi 2 tab cùng lúc ghi đè buffer của nhau, vốn là lỗi tiềm ẩn của kiến trúc cũ trước CP3).
- Hàm thuần tuý (không cần state) để tái sử dụng ở chế độ batch (`diagnosis_service.py`): `compute_bpm`, `compute_sdnn`, `compute_rmssd`, `rr_to_ms`.

#### 3.3. Nối vào luồng real-time (`backend/service/data_streamer.py`, `backend/service/inference_service.py`, `backend/api/ws_routes.py`)
1. `data_streamer.ecg_file_reader()`: đọc cả bản ghi 1 lần → lọc (`bandpass_filter` + `notch_filter`) 1 lần → `pan_tompkins_r_peaks` 1 lần (trên tín hiệu GỐC 360Hz, nơi đã kiểm chứng 97% F1) → `resample_signal` 1 lần (360→125Hz) + quy đổi chỉ số đỉnh R sang miền 125Hz. Sau đó **stream điểm-theo-điểm** như cũ (10 điểm/gói, 36 FPS) để vẽ biểu đồ mượt, nhưng chỉ khi luồng "đi qua" đúng vị trí 1 đỉnh R (so trên trục 360Hz gốc) mới cắt 1 nhịp (`extract_beat_window` trên miền 125Hz) và tính `HRVTracker.update()`.
2. `inference_service.predict(beat_window)`: **không lọc lại** (đã lọc ở bước 1, và sau resample fs thực tế không còn là 360Hz nữa nên lọc lại bằng fs=360 sẽ sai) — chỉ gọi `normalize_window()` rồi đưa vào model. Đây là điểm dễ gây bug nhất nếu có người thêm 1 nguồn dữ liệu mới trong tương lai mà quên tuân theo hợp đồng "đầu vào phải đã lọc + đúng miền 125Hz + đã pad/truncate 187 điểm".
3. `ws_routes.py`: AI + BPM/HRV chỉ tính lại đúng lúc có nhịp mới (`beat_info is not None`), **giữ nguyên giá trị gần nhất giữa 2 nhịp** (sample-and-hold) để Dashboard luôn có dữ liệu hiển thị. `heatmap` là ngoại lệ — chỉ khác `null` đúng ở gói tin vừa chẩn đoán (giữ nguyên ngữ nghĩa cũ: "heatmap khác null = vừa có 1 sự kiện bất thường mới cần log", để không phải sửa gì ở `AnomalyContext`/`DashboardPage` phía frontend).

#### 3.4. API mới
- **`GET /api/records`** (`backend/api/records_routes.py`): quét `data/raw/physionet_mitdb/` (cặp `.hea`+`.dat`), trả về:
  ```jsonc
  { "default_record": "208", "count": 48, "records": [
      { "id": "100", "description": "Nhịp xoang bình thường - phù hợp demo baseline", "is_default": false },
      { "id": "208", "description": "Ngoại tâm thu thất (PVC) tần suất rất cao (mặc định khi stream)", "is_default": true },
      ... // 8 bản ghi có mô tả lâm sàng curated (100,119,200,207,208,213,217,234), còn lại mô tả mặc định "Bản ghi MIT-BIH #<id>"
  ]}
  ```
  - Đổi bản ghi đang stream: mở lại `WS /ws/ecg?record=<id>` (client tự đóng/mở kết nối — không dùng lệnh 2 chiều qua WS để tránh phức tạp/race-condition). `record_exists()` validate chống path traversal (chặn `/`, `\`, `..` trong query param).
- **`POST /api/diagnosis/upload-ecg?fs=360`** (`backend/api/diagnosis_routes.py`, `backend/service/diagnosis_service.py`): nhận file CSV 1 cột biên độ (có/không header, tách bằng `,` hoặc `;`, lấy CỘT CUỐI nếu nhiều cột), tối thiểu 2 giây dữ liệu. Chạy full pipeline (lọc → R-peak → cắt nhịp → AI) trên toàn bộ file, trả về:
  ```jsonc
  {
    "total_beats": int, "duration_seconds": float,
    "class_counts": {"BÌNH THƯỜNG": int, ...}, "class_percentages": {...},
    "bpm": {"avg": float, "min": float, "max": float},
    "hrv": {"sdnn_ms": float, "rmssd_ms": float},
    "anomalies": [{"beat_index": int, "r_peak_sample": int, "time_seconds": float, "prediction": str}, ...],  // tối đa 500 mục
    "anomalies_total": int, "anomalies_truncated": bool,
    "overall_assessment": "Phát hiện X/Y nhịp bất thường (Z%), chủ yếu là '...' (N nhịp)."  // rule-based, KHÔNG phải LLM
  }
  ```
  - Cố tình **không trả heatmap** cho từng nhịp bất thường (báo cáo có thể có hàng trăm/nghìn nhịp lỗi, heatmap từng nhịp sẽ phình quá lớn) — muốn xem XAI chi tiết 1 nhịp thì dùng luồng real-time + trang XAI hiện có.
  - Cố tình **chưa có tóm tắt bằng LLM** — thuộc CP 4.2 (Trợ lý AI Tạo Báo Cáo Lâm Sàng), để dành tránh chồng lấn phạm vi.
  - Chỉ hỗ trợ CSV (chưa `.dat`/`.edf`) — đủ dùng cho demo, mở rộng format là việc nhỏ có thể làm sau nếu cần.

#### 3.5. Công cụ kiểm thử đã xây dựng (`backend/scripts/`)
| Script | Chạy bằng | Đo gì |
|:---|:---|:---|
| `validate_qrs.py` | `python -m backend.scripts.validate_qrs [record_id ...]` | Độ chính xác phát hiện đỉnh R so nhãn bác sĩ (Precision/Recall/F1) |
| `validate_classification.py` | `python -m backend.scripts.validate_classification [record_id ...]` | Độ chính xác chẩn đoán **end-to-end** (raw signal → AAMI) so nhãn bác sĩ, kèm confusion matrix |
| `test_ws.py` | `python -m backend.scripts.test_ws [record_id] [so_goi_tin]` | Xem payload WebSocket thực tế (cần server đang chạy) |
| `test_inference.py` (thư mục gốc) | `python test_inference.py` | Smoke test nhanh, không cần server |

**Dùng 2 script `validate_*` sau MỌI thay đổi ở `qrs_detector.py`/`signal_processing.py`/`inference_service.py`/`data_streamer.py`** — đây là cách duy nhất để biết pipeline có còn đúng hay không, đừng chỉ test bằng mắt qua vài gói WebSocket (bài học từ mục 3.1).

#### 3.6. ⏳ CP 3.6 — Nối Frontend với API mới của CP3 (CHƯA LÀM — phần dễ nhất để bắt đầu track Frontend)
Frontend hiện tại (`StatCards.jsx`, `DashboardPage.jsx`, `App.jsx`) **hoàn toàn chưa biết** đến `bpm`, `hrv_sdnn`, `hrv_rmssd`, `is_new_beat`, `GET /api/records`, hay `POST /api/diagnosis/upload-ecg`. Cần:
- `StatCards.jsx`: thêm 1-2 ô hiển thị BPM tức thời + HRV (SDNN), đọc trực tiếp từ payload WS đã có sẵn field này — **không cần sửa backend gì thêm**.
- Dropdown chọn bản ghi (component mới, vd `RecordSelector.jsx`): gọi `GET /api/records` lúc mount, khi user chọn → đóng WS cũ, mở `ws://.../ws/ecg?record=<id>` mới (sửa `DashboardPage.jsx`'s `connect()` để nhận `record` từ state thay vì hardcode).
- Form upload (trang mới hoặc modal): gọi `POST /api/diagnosis/upload-ecg` bằng `FormData`, hiển thị báo cáo trả về (bảng `class_counts`, `bpm`, `hrv`, danh sách `anomalies`).

Đây là task **độc lập, không phụ thuộc ai khác**, nên làm đầu tiên khi bắt đầu track Frontend (xem [pccv.md](pccv.md) — Track A, Sprint 2 tuần 1).

#### 3.7. Sub-checkpoints
- [x] **CP 3.1** DSP Preprocessing Module (`signal_processing.py`)
- [x] **CP 3.2** Dynamic R-Peak Detector (`qrs_detector.py`) — F1 97.14%
- [x] **CP 3.3** HRV & Exact BPM Engine (`hrv.py`) + wiring — Accuracy end-to-end 94.33%
- [x] **CP 3.4** Patient Record Switcher API (`records_routes.py`)
- [x] **CP 3.5** File Upload & Offline Diagnosis API (`diagnosis_routes.py`, `diagnosis_service.py`)
- [x] **CP 3.6** Nối Frontend với API CP3 (`RecordSelector.jsx`, cập nhật `StatCards.jsx`/`DashboardPage.jsx`, form upload)

---

### 🟡 CHECKPOINT 4: NGHIỆP VỤ Y TẾ LÂM SÀNG, BÁO CÁO THÔNG MINH (AI REPORT) & HỆ THỐNG CẢNH BÁO
> **Trọng tâm**: Nâng cấp giao diện người dùng thành phần mềm trạm điều dưỡng/bác sĩ thực thụ. **Toàn bộ Checkpoint này là Frontend** (trừ 1 API nhỏ tuỳ chọn ở CP4.5), không phụ thuộc Checkpoint 5 — có thể làm song song.
> **Quyết định phạm vi quan trọng** (đọc trước khi làm): để giữ mọi sub-checkpoint độc lập và không phải chờ CP5 (database), **toàn bộ dữ liệu Bệnh nhân/Cài đặt ở Checkpoint này lưu tạm ở `localStorage`** giống cách `AnomalyContext` đang làm — KHÔNG chờ database thật. Khi CP5.1 xong, sẽ có 1 task nhỏ riêng để "di cư" localStorage → API thật (không nằm trong CP4).

#### 4.1. Hiện trạng & hạn chế
- Tab "Hồ sơ bệnh nhân" (`patient`) và "Cài đặt" (`settings`) trong `App.jsx` hiện chỉ render 1 `<div>` tĩnh ghi "tính năng đang được phát triển".
- Cảnh báo hiện chỉ có highlight màu trên `StatCards`/`ECGChart` (`isDanger`, dải đỏ mờ) — chưa có âm thanh, chưa phân cấp mức độ nguy hiểm.
- Chưa có xuất báo cáo (PDF/CSV).
- `AnomalyContext` giới hạn 20 sự kiện gần nhất, mất khi F5 (chấp nhận được cho tới khi có CP5 database).

#### 4.2. CP 4.1 — Patient Management UI
**File**: `frontend/src/pages/PatientPage.jsx` (thay div placeholder trong `App.jsx`), `frontend/src/context/PatientContext.jsx` (mới, cùng pattern với `AnomalyContext.jsx`), `frontend/src/components/patient/PatientForm.jsx`, `PatientCard.jsx`.

**Data model** (lưu `localStorage` key `ecg_patients`, mảng JSON):
```js
{ id: crypto.randomUUID(), name: "", age: 0, gender: "M|F|Other",
  bedNumber: "", admissionDate: "ISO date", diagnosis: "",  // tiền sử bệnh, free text
  attendingDoctor: "", vitals: { bloodPressure: "120/80", spo2: 98 },
  activeRecordId: "208" }  // gắn với 1 bản ghi PhysioNet đang stream cho giường này (id từ GET /api/records, CP3.4)
```
**Yêu cầu chức năng**:
- CRUD đầy đủ (thêm/sửa/xoá/xem), validate: `name` bắt buộc, `age` 0-120, `bedNumber` không trùng giữa các bệnh nhân đang active.
- Giao diện lưới nhiều giường (Multi-bed Monitoring View): mỗi `PatientCard` hiển thị tên/giường/trạng thái nhịp gần nhất; bấm vào 1 card → chuyển `Dashboard` sang stream đúng `activeRecordId` của bệnh nhân đó (tái dùng cơ chế đổi record đã làm ở CP3.6 — **phụ thuộc CP3.6 xong trước**, xem ma trận phụ thuộc trong `pccv.md`).
- **Định nghĩa hoàn thành (DoD)**: CRUD hoạt động, dữ liệu còn sau F5, bấm 1 bệnh nhân đổi đúng luồng stream.

#### 4.3. CP 4.2 — Hệ thống Cảnh báo Đa Tầng (Multi-Tier Alarm System)
**File**: `frontend/src/constants/alarmLevels.js` (mới — bảng ánh xạ nhãn AAMI → mức độ), `frontend/src/utils/alarmAudio.js` (mới — Web Audio API), mở rộng `AnomalyContext.jsx` hoặc `AlarmContext.jsx` (mới) để giữ trạng thái mute/snooze.

**Bảng phân cấp mức độ nguy hiểm** (định nghĩa cứng, dùng chung toàn hệ thống — đặt trong `alarmLevels.js` để chỉ sửa 1 chỗ):
| Mức | Màu | Nhãn AAMI tương ứng | Hành vi |
|:---:|:---:|:---|:---|
| 1 | 🟢 Bình thường | `BÌNH THƯỜNG` (N) | Không cảnh báo |
| 2 | 🟡 Chú ý | `CẢNH BÁO: TRÊN THẤT (S)`, `CẢNH BÁO: CHƯA RÕ (Q)` | Highlight vàng, không âm thanh |
| 3 | 🔴 Khẩn cấp | `CẢNH BÁO: NHỊP THẤT (V)`, `CẢNH BÁO: HỢP NHẤT (F)` | Highlight đỏ + âm thanh + push notification |

- Âm thanh: dùng `OscillatorNode` (Web Audio API, không cần file mp3) phát chuỗi beep theo mẫu chuẩn IEC 60601-1-8 (vd: 1 beep/giây cho mức 2, cụm 3 beep liên tiếp mỗi 2 giây cho mức 3).
- Mute/Snooze: nút trên `Header.jsx`, tắt âm thanh **2 phút** rồi tự bật lại (chuẩn y tế — không cho tắt vĩnh viễn để tránh rủi ro lâm sàng), có đếm ngược hiển thị.
- Browser Push Notification: `Notification` API, xin quyền ở trang Cài đặt (CP4.5), chỉ bắn cho mức 3.
- **DoD**: nhịp V/F thật (từ dashboard đang chạy record 208) kích hoạt âm thanh + notification, nút mute hoạt động đúng 2 phút.

#### 4.4. CP 4.3 — Xuất Báo Cáo Y Tế (Medical Report Exporter)
**Quyết định kiến trúc**: làm **hoàn toàn ở Frontend** (không cần backend mới) — dùng `jspdf` + `html2canvas` (thêm vào `frontend/package.json`), lấy dữ liệu trực tiếp từ `AnomalyContext`/`PatientContext` đang có sẵn trong session. Lý do: giữ CP4 độc lập hoàn toàn với backend/CP5.

**File**: `frontend/src/utils/reportGenerator.js`, `frontend/src/components/ReportButton.jsx` (đặt ở Header hoặc XAIPage).

**Nội dung PDF**: header thông tin bệnh nhân (từ `PatientContext`), snapshot `ECGChart` hiện tại (`html2canvas` chụp DOM), snapshot heatmap Grad-CAM của nhịp đang chọn ở `XAIPage`, bảng thống kê số lần xuất hiện mỗi loại nhịp trong `anomalyHistory`.
**CSV**: serialize thẳng `anomalyHistory` (không cần thư viện, dùng `Blob` + `URL.createObjectURL`).
**DoD**: bấm nút tải về được 1 file PDF có nội dung đọc được + 1 file CSV mở được bằng Excel.

#### 4.5. CP 4.4 — AI Diagnostic Explainer (Contextual XAI) — bản rút gọn có chủ đích
**Giới hạn phạm vi rõ ràng (quan trọng)**: đo chính xác khoảng PR/QRS/ST theo mili-giây đòi hỏi thuật toán phân đoạn từng sóng P/Q/R/S/T riêng biệt (wave delineation) — đây là 1 bài toán DSP lớn, khó hơn cả việc phát hiện đỉnh R (CP3.2), và **không nằm trong phạm vi CP4**. Vì vậy CP4.4 chỉ làm bản rút gọn, hoàn toàn ở Frontend, không cần API mới:
- Bảng tra cứu tĩnh (`frontend/src/constants/clinicalExplanations.js`) ánh xạ mỗi nhãn AAMI → đoạn giải thích lâm sàng mẫu chung (vd nhịp V: "Ngoại tâm thu thất — phức bộ QRS thường dãn rộng >120ms, không có sóng P đi trước...").
- Vùng highlight đỏ đã có sẵn trên `ECGChart.jsx` (dải `shapes` rect) + heatmap Bar trên `XAIPage.jsx` — chỉ cần làm rõ chú thích ("vùng AI tập trung chú ý nhất") thay vì con số PR/QRS/ST đo chính xác.
- Nếu sau này muốn đo thật (PR/QRS/ST theo ms), đó sẽ là 1 checkpoint DSP riêng trong tương lai, không phải CP4.4.
- **DoD**: chọn 1 nhịp bất thường ở `XAIPage`, thấy đoạn giải thích lâm sàng tương ứng với đúng nhãn của nhịp đó.

#### 4.6. CP 4.5 — Settings & Calibration Page
**File**: `frontend/src/pages/SettingsPage.jsx` (thay placeholder), lưu `localStorage` key `ecg_settings`.
- Cấu hình địa chỉ WebSocket server (mặc định `ws://localhost:8000`), dark/light mode auto theo giờ hoặc theo `prefers-color-scheme`.
- Nút xin quyền Browser Notification (dùng ở CP4.2).
- **Ngưỡng nhạy AI (Sensitivity threshold)**: hiện backend `predict()` chỉ trả nhãn `argmax`, **chưa có xác suất/độ tin cậy** để áp ngưỡng — dựng UI trước, nhưng cần 1 thay đổi backend rất nhỏ để có tác dụng thật:
  > **Yêu cầu chéo track (báo cho người làm Backend/CP5 sớm, việc này ~10-15 phút)**: thêm `confidence: float` (softmax probability của lớp dự đoán) vào tuple trả về của `ai_service.predict()` trong `backend/service/inference_service.py`, và thêm field `confidence` vào payload WS ở `ws_routes.py`. Không có thay đổi này, ô "ngưỡng nhạy" ở Settings chỉ mang tính giao diện (không có tác dụng thật). Ghi chi tiết yêu cầu này ở `pccv.md`.
- **DoD**: đổi setting → dashboard áp dụng ngay (vd đổi dark/light), Notification permission xin được, setting còn sau F5.

#### 4.7. Sub-checkpoints
- [x] **CP 4.1** Patient Management UI & Form Validation (`PatientPage.jsx`, `PatientContext.jsx`)
- [x] **CP 4.2** Medical Audio & Visual Alarm System (`alarmAudio.js`, `alarmLevels.js`)
- [ ] **CP 4.3** Automated Medical Report Generator (PDF/CSV, frontend-only)
- [ ] **CP 4.4** AI Diagnostic Explainer — bản rút gọn (bảng tra cứu tĩnh, không đo PR/QRS/ST thật)
- [ ] **CP 4.5** Settings & Calibration Page (+ yêu cầu chéo track: thêm `confidence` vào backend)

---

### 🟡 CHECKPOINT 5: HỆ THỐNG CƠ SỞ DỮ LIỆU, XÁC THỰC BẢO MẬT & PHÂN QUYỀN (RBAC)
> **Trọng tâm**: Chuyển từ Demo bộ nhớ tạm (In-Memory/LocalStorage) sang hệ thống có cơ sở dữ liệu bền vững + bảo mật. **Toàn bộ Checkpoint này là Backend** (trừ CP5.5 là điểm nối với Frontend), độc lập với Checkpoint 4 — có thể làm song song.

#### 5.1. Hiện trạng & hạn chế
- Mọi sự kiện bất thường chỉ lưu tạm ở `AnomalyContext` (React, mất khi F5, không chia sẻ giữa nhiều máy/nhiều người xem).
- Chưa có đăng nhập — ai mở app cũng xem/cấu hình được hết.
- Thiếu Audit Trail (bắt buộc với phần mềm y tế theo tinh thần HIPAA/HL7 — dự án không cần tuân thủ thật, nhưng nên có cho đúng chuẩn thiết kế).

#### 5.2. CP 5.1 — Database Schema & SQLAlchemy ORM — ✅ Hoàn thành 2026-08-30
**Quyết định công nghệ**: **SQLite** cho giai đoạn dev (file-based, zero-config, đủ cho demo/đồ án — không cần dựng PostgreSQL server). File DB: `backend/db/ecg_system.db` (đã thêm vào `.gitignore`, KHÔNG commit). ORM: SQLAlchemy 2.0.52 (style `Mapped`/`mapped_column` mới, không dùng `declarative_base()` cũ). Migration: Alembic 1.13.3.

**Đã cài đặt**:
- `backend/db/base.py`: `Base(DeclarativeBase)` dùng chung cho mọi model.
- `backend/db/models.py`: đủ 5 bảng đúng schema bên dưới, dùng `enum.Enum` (`UserRole`, `ReviewStatus`) cho các cột ENUM thay vì string thô, có `relationship()` 2 chiều đầy đủ giữa các bảng (`Patient.ecg_records`, `Patient.anomaly_events`, `AnomalyEvent.reviewer`, `User.reviewed_anomalies`, `User.audit_trails`, ...) và index trên mọi cột sẽ dùng để lọc ở CP5.3 (`patient_id`, `record_id`, `prediction_label`, `timestamp_ms`).
- `backend/db/session.py`: `engine` + `SessionLocal` + dependency `get_db()` cho FastAPI (`check_same_thread=False` khi SQLite, không ảnh hưởng nếu sau này đổi Postgres).
- `backend/core/config.py`: thêm `DATABASE_URL` vào `Settings` (mặc định `sqlite:///./backend/db/ecg_system.db`) — đổi qua biến môi trường khi cần chuyển Postgres ở CP6.3, không phải sửa code.
- `alembic.ini` (gốc repo) + `backend/db/migrations/` (`env.py` đã sửa để đọc model từ `Base.metadata` và lấy connection string từ `settings.DATABASE_URL` thay vì hardcode) + 1 migration khởi tạo (`versions/9840408bc1c5_initial_schema_*.py`) tự sinh bằng `alembic revision --autogenerate`, đã kiểm chứng cả 2 chiều `upgrade head` và `downgrade base` chạy sạch, đúng thứ tự phụ thuộc khoá ngoại.
- `backend/scripts/validate_db.py` (script kiểm thử, theo đúng pattern `validate_qrs.py`/`validate_classification.py` ở CP3): tạo DB SQLite in-memory riêng, insert đủ 5 bảng + xác nhận quan hệ 2 chiều hoạt động đúng (`patient.anomaly_events`, `anomaly.reviewer`, `doctor.reviewed_anomalies`, cột JSON `heatmap` đọc/ghi đúng). Chạy: `python -m backend.scripts.validate_db`.
- **DoD đã đạt**: `alembic upgrade head` tạo đúng 5 bảng (xác nhận bằng `sqlite3` trực tiếp), `validate_db.py` chạy xanh toàn bộ assertion.

**File**: `backend/db/models.py`, `backend/db/session.py` (engine + `SessionLocal` + dependency `get_db()` cho FastAPI), `backend/db/migrations/` (Alembic).

**Schema (5 bảng)**:
```
users            id PK, username UNIQUE, email, hashed_password, role ENUM(admin,doctor,nurse), created_at
patients         id PK, name, age, gender, bed_number, admission_date, diagnosis, attending_doctor,
                 active_record_id, created_at, updated_at
ecg_records      id PK, patient_id FK->patients, physionet_record_id, started_at, ended_at
anomaly_events   id PK, patient_id FK->patients, record_id FK->ecg_records, prediction_label,
                 confidence FLOAT, heatmap JSON, r_peak_sample INT, timestamp_ms BIGINT,
                 reviewed_by FK->users (nullable), review_status ENUM(pending,approved,corrected) DEFAULT pending,
                 corrected_label (nullable)
audit_trails     id PK, user_id FK->users, action, target_type, target_id, detail JSON, timestamp
```
- **DoD**: `alembic upgrade head` tạo đủ 5 bảng trên SQLite trống, có ít nhất 1 test insert/query qua SQLAlchemy session chạy được.

#### 5.3. CP 5.2 — Authentication & Authorization APIs — ✅ Hoàn thành 2026-08-30
**File**: `backend/api/auth.py`, `backend/core/security.py`.

**Lệch nhẹ so với đề xuất công nghệ ban đầu (có chủ đích)**: dùng **`PyJWT`** thay vì `python-jose`, và gọi thẳng thư viện **`bcrypt`** thay vì qua `passlib[bcrypt]`. Lý do: `python-jose` gần đây ít được bảo trì tích cực; `passlib` có xung đột phiên bản đã biết với `bcrypt>=4.1` (passlib tự dò version bcrypt bằng cách gọi API đã bị đổi, ném lỗi ở một số tổ hợp phiên bản) — gọi thẳng `bcrypt.hashpw`/`bcrypt.checkpw` tránh hẳn lớp bọc trung gian này. Hành vi bên ngoài (API contract) không đổi so với spec ban đầu.

**API contract (CỐ ĐỊNH — đây là hợp đồng Frontend sẽ build theo, xem `pccv.md` để biết cách Frontend mock trước khi API thật xong)**:
```
POST /api/auth/login
  body: { "username": string, "password": string }
  200: { "access_token": string, "refresh_token": string, "token_type": "bearer", "role": "admin"|"doctor"|"nurse" }
  401: { "detail": "Sai tài khoản hoặc mật khẩu" }

POST /api/auth/refresh
  body: { "refresh_token": string }
  200: { "access_token": string, "token_type": "bearer" }

GET /api/auth/me
  header: Authorization: Bearer <access_token>
  200: { "id": int, "username": string, "role": string }
  401: { "detail": "Token không hợp lệ hoặc hết hạn" }
```
- Middleware: `get_current_user` (FastAPI dependency, decode JWT từ header), `require_role(*roles)` (dependency factory, trả 403 nếu role không khớp) — áp vào các endpoint cần bảo vệ ở CP5.3/5.4.
- **Chi tiết token**: access token (30 phút, claim `sub`/`username`/`role`/`type=access`) và refresh token (7 ngày, chỉ claim `sub`/`type=refresh`) đều là JWT ký `HS256` bằng `JWT_SECRET_KEY` (đã thêm vào `Settings`, mặc định là secret CHỈ DÙNG DEV — bắt buộc đổi qua biến môi trường trước khi triển khai thật). Refresh token cố tình KHÔNG mang theo `role` — lúc `/api/auth/refresh` luôn đọc lại role hiện tại từ DB, để nếu tài khoản bị đổi quyền thì access token mới cấp phản ánh đúng quyền mới nhất, không dùng quyền cũ lúc đăng nhập. Có kiểm tra claim `type` để access token không thể bị dùng thay refresh token và ngược lại.
- **`backend/scripts/seed_users.py`** (mới): tạo sẵn 3 tài khoản test — `admin/Admin@123` (admin), `bs_hai/Doctor@123` (doctor), `dd_lan/Nurse@123` (nurse) — Track Frontend (CP5.5) dùng ngay để test đủ 3 role. Chạy: `python -m backend.scripts.seed_users` (idempotent, chạy lại không tạo trùng).
- **`backend/scripts/validate_auth.py`** (mới, theo pattern `validate_qrs.py`): dùng FastAPI `TestClient` kiểm tra toàn bộ 18 trường hợp — login đúng/sai mật khẩu/sai username, `/me` với token hợp lệ/thiếu/giả, `/refresh` hợp lệ + từ chối khi đưa nhầm access token vào chỗ refresh token, và `require_role("admin")` từ chối role `doctor` (403)/chấp nhận role `admin` (200) qua 1 route test riêng (không đụng vào `main.py` thật). Chạy: `python -m backend.scripts.seed_users` trước, rồi `python -m backend.scripts.validate_auth`.
- **DoD đã đạt**: toàn bộ 18 assertion trong `validate_auth.py` xanh.

#### 5.4. CP 5.3 — Historical Anomaly Query & Pagination APIs — ✅ Hoàn thành 2026-08-30
**File**: `backend/api/anomalies.py`, `backend/service/anomaly_log_service.py` (mới).
```
GET /api/anomalies?patient_id=&from=&to=&label=&page=1&page_size=20
  header: Authorization: Bearer <token>  (mọi role đã login đều xem được)
  200: { "total": int, "page": int, "page_size": int, "items": [ {...anomaly_event...} ] }
```
- `from`/`to`: ISO 8601 (vd `2026-08-30T00:00:00Z`); nếu không có timezone thì coi như UTC (không phụ thuộc múi giờ máy chạy server). Sắp xếp `timestamp_ms` giảm dần (mới nhất trước). `items` KHÔNG kèm `heatmap` (tránh payload phình to khi phân trang) — xem chi tiết XAI 1 sự kiện qua luồng real-time hiện có.

**Vấn đề kiến trúc phát sinh khi làm (đã giải quyết)**: `anomaly_events`/`ecg_records` bắt buộc phải có `patient_id` hợp lệ (khoá ngoại), nhưng CP4.1 (Patient Management) vẫn đang lưu localStorage ở Frontend, CHƯA có API tạo `Patient` thật trong Database — nghĩa là chưa có cách nào tạo được 1 dòng `patients` hợp lệ khi CP5.3 cần ghi log. Giải quyết bằng `backend/service/anomaly_log_service.py::resolve_patient()`: `/ws/ecg` nhận thêm query param **tuỳ chọn** `patient_id` — nếu không truyền (hoặc truyền id không tồn tại), tự dùng 1 "bệnh nhân mặc định" (`(Chưa gán bệnh nhân)`, tự tạo 1 lần nếu chưa có). Khi CP4.1 có API bệnh nhân thật, Frontend chỉ cần truyền đúng `patient_id` qua query param, không cần sửa gì ở backend.
- Mỗi khi mở `WS /ws/ecg`: tạo 1 dòng `ecg_records` mới (`start_ecg_record`), đóng lại `ended_at` khi ngắt kết nối (`end_ecg_record`, chạy trong `finally`).
- Mỗi khi phát hiện 1 nhịp bất thường (heatmap khác `None`, đúng ngữ nghĩa cũ): ghi 1 dòng `anomaly_events` (`log_anomaly`) kèm `confidence` thật (xem mục dưới).
- **Nhân tiện hoàn thành luôn "yêu cầu chéo track #1"** đã ghi trong `pccv.md`: `ai_service.predict()` giờ trả về 4 giá trị `(label, heatmap, latency_ms, confidence)` thay vì 3 (softmax probability của lớp được chọn) — CP4.5 (ngưỡng nhạy AI) dùng được ngay, không cần chờ thêm. Đã cập nhật đồng bộ mọi nơi gọi `predict()`: `ws_routes.py` (thêm field `confidence` vào payload WS), `diagnosis_service.py` (thêm `confidence` vào từng mục `anomalies` của báo cáo offline — bổ sung so với spec CP3.5 gốc, tương thích ngược), `test_inference.py`, `validate_classification.py`.
- **`backend/scripts/validate_anomalies.py`** (mới): mở 1 phiên WebSocket THẬT (record 208) qua FastAPI `TestClient` để `ws_routes.py` tự ghi anomaly thật vào DB, rồi kiểm tra 25 assertion — xác thực bắt buộc (401 nếu thiếu token), lọc đúng theo `patient_id`/`label`/khoảng thời gian (kể cả 2 trường hợp biên: lọc tương lai → rỗng, lọc quá khứ xa → vẫn thấy), và phân trang đúng (`page_size=1` không lặp item giữa các trang). Chạy: `python -m backend.scripts.validate_anomalies` (mất ~8-10s vì phải chờ dữ liệu WS thật, không rút ngắn được).
- **Phụ thuộc**: cần CP5.1 (bảng `anomaly_events`) xong trước — đã có.
- **DoD đã đạt**: toàn bộ 25 assertion trong `validate_anomalies.py` xanh.

#### 5.5. CP 5.4 — Doctor Feedback & Human-in-the-Loop API — ✅ Hoàn thành 2026-08-30
**File**: `backend/api/anomalies.py` (thêm route vào cùng router đã có ở CP5.3).
```
POST /api/anomalies/{id}/verify
  body: { "status": "approved"|"corrected", "corrected_label"?: string }
  yêu cầu role: doctor hoặc admin (require_role("doctor","admin"))
  200: { ...anomaly_event đã cập nhật, kèm reviewed_by... }
  401: chưa đăng nhập | 403: role không phải doctor/admin | 404: không tìm thấy anomaly
  422: status="corrected" mà thiếu corrected_label, hoặc corrected_label không thuộc 5 nhãn AAMI hợp lệ
```
- Ghi audit trail (`audit_trails`) mỗi lần verify **thành công** (đủ quyền + qua validate): ai xác nhận (`user_id`), lúc nào (`timestamp` mặc định `now()`), kết quả gì (`detail` JSON chứa `status`+`corrected_label`). Verify lại 1 sự kiện đã verify trước đó vẫn được phép (ghi đè trạng thái mới nhất trên `anomaly_events`), nhưng lịch sử đầy đủ từng lần vẫn còn nguyên trong `audit_trails` (không ghi đè).
- `corrected_label` bắt buộc phải là 1 trong 5 nhãn AAMI hợp lệ (validate theo `AAMI_CLASSES` của `inference_service.py`, không chấp nhận chuỗi tự do) — đảm bảo dữ liệu bác sĩ sửa (`review_status=corrected`) sạch, sẵn sàng làm nền cho Active Learning/retrain tương lai. **Không làm retrain thật trong checkpoint này**, chỉ cần lưu đúng.
- **`backend/scripts/validate_review.py`** (mới): tạo 1 `anomaly_events` test trực tiếp qua ORM (không cần mở WS thật — đường ghi log đã được `validate_anomalies.py` kiểm chứng riêng), rồi kiểm tra 16 assertion: nurse bị từ chối (403), thiếu token (401), doctor/admin verify được (200, `review_status`/`reviewed_by`/`corrected_label` đúng), thiếu/sai `corrected_label` bị từ chối (422), id không tồn tại (404), và `audit_trails` ghi đủ đúng 3 lần verify thành công (2 lần thất bại do 403/401/422 KHÔNG được ghi audit).
- **DoD đã đạt**: toàn bộ 16 assertion trong `validate_review.py` xanh; chạy lại `validate_anomalies.py` không hồi quy.

#### 5.6. CP 5.5 — Frontend Auth Guard & Role-based UI (ĐIỂM NỐI 2 TRACK)
**File**: `frontend/src/pages/LoginPage.jsx`, `frontend/src/context/AuthContext.jsx`, `frontend/src/components/AuthGuard.jsx`.
- Trang đăng nhập gọi `POST /api/auth/login`, lưu token (khuyến nghị: `localStorage` cho đơn giản ở giai đoạn demo — ghi rõ đây KHÔNG phải best practice bảo mật production, httpOnly cookie mới chuẩn, nhưng đủ cho đồ án).
- `AuthGuard`: bọc quanh `App.jsx`, chưa có token hợp lệ → chỉ render `LoginPage`.
- Ẩn/hiện tab theo role (vd tab "Cài Đặt Hệ Thống" chỉ `admin` mới thấy, nút "Sửa nhãn" ở XAIPage chỉ `doctor` mới thấy).
- **Đây là task DUY NHẤT bắt buộc chờ người kia** — người làm Frontend (CP4) làm task này **sau khi** CP5.2 xong (hoặc build song song bằng cách mock đúng response shape ở mục 5.3 rồi cắm API thật vào sau — khuyến khích làm cách này để không bị block, chi tiết ở `pccv.md`).
- **DoD**: chưa login không vào được app, login đúng role thấy đúng menu, token hết hạn tự về LoginPage.

#### 5.7. Sub-checkpoints
- [x] **CP 5.1** Database Schema & SQLAlchemy ORM (`backend/db/`) — Hoàn thành 2026-08-30
- [x] **CP 5.2** Authentication & Authorization APIs (`backend/api/auth.py`) — Hoàn thành 2026-08-30
- [x] **CP 5.3** Historical Anomaly Query & Pagination APIs (+ ghi anomaly vào DB từ `ws_routes.py`) — Hoàn thành 2026-08-30
- [x] **CP 5.4** Doctor Feedback & Human-in-the-Loop API — Hoàn thành 2026-08-30
- [ ] **CP 5.5** Frontend Auth Guard & Role-based UI *(điểm nối 2 track — xem `pccv.md`)*

---

### 🟡 CHECKPOINT 6: TỐI ƯU EDGE AI, ĐÓNG GÓI DOCKER, CI/CD & KIỂM THỬ TOÀN DIỆN
> **Trọng tâm**: Tối ưu hiệu năng mô hình, đóng gói Docker, tự động hoá kiểm thử. Chủ yếu **Backend/Hạ tầng**, phần test frontend (Vitest) là phần việc nhỏ của người làm Frontend, viết test cho chính phần mình làm.

#### 6.1. CP 6.1 — PyTorch → ONNX & Quantization — ✅ Hoàn thành 2026-08-30
**File**: `src/models/export_onnx.py`, `src/models/onnx_runner.py` (predictor tối giản dùng ONNX Runtime để đo accuracy), `backend/scripts/validate_onnx_classification.py`, `docs/onnx_comparison.md`.

- Xuất `saved_models/resnet1d.onnx` (FP32) bằng `torch.onnx.export(..., dynamo=False)` — PyTorch 2.x mặc định dùng exporter mới dựa trên `torch.export`/dynamo (cần thêm package `onnxscript`); dùng thẳng exporter kiểu cũ (TorchScript-based) cho kiến trúc không có control-flow động như ResNet1D, tránh thêm dependency.
- **⚠️ Điều chỉnh tiêu chí kiểm chứng sai số (có lý do rõ ràng)**: ngưỡng sai số tuyệt đối 1e-5 trên logit thô đề xuất ban đầu **không phù hợp** — đo thực tế trên 200 batch ngẫu nhiên cho sai số tuyệt đối lớn nhất ~2.4e-4 (do tích luỹ sai số dấu phẩy động qua nhiều lớp Conv/BatchNorm giữa 2 backend toán học khác nhau — PyTorch dùng MKL/oneDNN, ONNX Runtime dùng kernel riêng), NHƯNG sai số tương đối chỉ ~1.3e-6 và **0/200 batch bị đổi lớp dự đoán (argmax)**. Đổi tiêu chí kiểm chứng (`verify_parity()`) thành: (a) lớp dự đoán phải khớp 100% (điều thực sự ảnh hưởng hành vi model) + (b) sai số tương đối < 1e-3 (đủ chặt để bắt bug logic export thật, không bị nhiễu bởi thang đo logit thô).
- Lượng hoá INT8 bằng `onnxruntime.quantization.quantize_dynamic` → `saved_models/resnet1d_int8.onnx`: **697.3KB, đạt đúng mục tiêu <700KB**.
- **⚠️ Phát hiện quan trọng (báo trung thực, không giấu)**: kỳ vọng ban đầu INT8 nhanh hơn 3-5 lần — thực tế đo trên CPU máy dev **INT8 chậm hơn cả FP32** (1.16ms vs 0.25ms), vì dynamic quantization tốn thêm phép quantize/dequantize activation tại runtime, chỉ thật sự nhanh hơn trên phần cứng có tập lệnh INT8 chuyên dụng (AVX512-VNNI, NPU edge...) — không có trên CPU dev thông thường. Ngược lại, **ONNX FP32 nhanh hơn PyTorch gốc 4.5 lần** (1.13ms → 0.25ms) mà không đổi gì về size/accuracy — xem phân tích đầy đủ trong `docs/onnx_comparison.md`.
- **Kiểm chứng accuracy end-to-end** (`validate_onnx_classification.py`, cùng 8 bản ghi + nhãn bác sĩ dùng ở CP3.3): ONNX FP32 = **94.33%** (giống hệt PyTorch baseline), ONNX INT8 = **94.18%** (rớt 0.15 điểm %, trong ngưỡng chấp nhận 2 điểm %).
- Đã thêm `onnx==1.17.0`, `onnxruntime==1.20.1` vào `requirements.txt`.
- **Lưu ý phạm vi**: checkpoint này CHỈ xuất + kiểm chứng model ONNX như 1 artifact sẵn sàng cho triển khai edge — KHÔNG đổi `backend/service/inference_service.py` sang chạy ONNX (service thật vẫn dùng PyTorch vì cần Grad-CAM cho XAI, ONNX Runtime không hỗ trợ backward pass; latency PyTorch hiện tại — 0.13-1.1ms — đã dư sức đáp ứng real-time nên không cần đổi).
- **DoD đã đạt**: `resnet1d.onnx` chạy được qua `onnxruntime`, lớp dự đoán khớp 100% với PyTorch trên 200 batch ngẫu nhiên; có bản quantized kèm bảng so sánh kích thước/latency/accuracy đầy đủ trong `docs/onnx_comparison.md`.

#### 6.2. CP 6.2 — Automated Test Suite
**Backend — ✅ Hoàn thành 2026-08-31** (`tests/`, `pytest.ini`, dùng `pytest`):
- `tests/conftest.py`: fixture dùng chung — DB test **cô lập hoàn toàn** với DB dev thật (SQLite `:memory:` + `StaticPool` để mọi session trong 1 phiên pytest dùng chung 1 connection, ghi đè dependency `get_db` của FastAPI qua `app.dependency_overrides` — **không sửa code production**); `client` (TestClient session-scoped, tránh nạp lại model AI ~1-2s cho mỗi test); `seeded_users`/`auth_headers` (3 tài khoản test/3 role, tách biệt hoàn toàn với tài khoản do `seed_users.py` tạo trên DB dev thật); các marker `requires_physionet_data`/`requires_saved_model`/`requires_onnx_model` để tự skip khi thiếu file gitignored (đúng tinh thần CP6.4: CI không có `data/raw/`/`saved_models/`).
  - ⚠️ Gặp lỗi `PermissionError` khi dùng `tmp_path_factory` (thư mục temp mặc định của pytest trên Windows) — chuyển hẳn sang SQLite in-memory, vừa né lỗi vừa không cần dọn file sau khi chạy. Đã xác nhận: chạy `pytest` không hề đụng tới `backend/db/ecg_system.db` (kiểm tra size/mtime file không đổi trước/sau).
- `tests/test_dsp.py`: `bandpass_filter`/`notch_filter` triệt tiêu đúng dải tần nhiễu (đo bằng tổng năng lượng FFT trong 1 dải tần thay vì 1 bin đơn lẻ — bin đơn dễ sai vì phụ thuộc độ phân giải FFT khớp chính xác tần số cần đo, đã tự vấp lỗi này lúc đầu với tone 0.1Hz trên cửa sổ 2s quá ngắn); `normalize_window` luôn trả về [0,1] + xử lý tín hiệu phẳng không chia cho 0.
- `tests/test_qrs.py`: bọc `validate_qrs.py::evaluate_record()` thành assertion `f1 > 0.90` cho record 100/213/234 (không assert 207/119 — biết trước khó, xem plan.md mục 3.2).
- `tests/test_model.py`: shape đầu ra `(batch, 5)`, chấp nhận input thiếu chiều channel, tổng softmax ≈ 1, ONNX vs PyTorch argmax khớp 100% (skip nếu chưa export ONNX).
- `tests/test_websocket.py`: mở WS `/ws/ecg` thật, kiểm tra đủ key trong payload JSON, và record không tồn tại tự fallback về mặc định thay vì lỗi.
- `tests/test_api.py`: `GET /api/records`, `POST /api/diagnosis/upload-ecg` (kèm test file quá ngắn bị từ chối 400), **cùng với auth** (sai mật khẩu, token giả, refresh token bị đưa nhầm) **và anomalies/verify** (401/403/422/404, lọc đúng, `corrected_label` phải hợp lệ) — mở rộng nhẹ so với spec ban đầu (chỉ nhắc records+diagnosis) vì đây đều là bề mặt API chưa có test tự động nào, không có lý do bỏ qua.
- **26/26 test xanh, chạy dưới 4 giây** (không cần dữ liệu MIT-BIH thật cho phần lớn test — DoD của CP6.4 "CI không có data/raw/" vẫn thoả vì các test cần nó tự skip).

**Frontend** (`frontend/src/**/*.test.jsx`, thêm `vitest` + `@testing-library/react` vào `package.json`) — ⏳ Track A tự làm:
- Test các component do chính người làm CP4 viết (`PatientForm`, `alarmAudio` logic thuần JS, `reportGenerator` CSV serializer).

**Quy ước**: mỗi người viết test cho phần mình phụ trách (Backend viết `tests/*.py`, Frontend viết `*.test.jsx`) — không ai phải hiểu sâu code của người kia để viết test.
**DoD**: `pytest` xanh hết (✅ đã đạt phần backend), `npm run test` (Vitest) xanh hết (Track A).

#### 6.3. CP 6.3 — Dockerization — ✅ Hoàn thành 2026-08-31
**File**: `backend.Dockerfile`, `frontend.Dockerfile`, `nginx.conf`, `docker-compose.yml`, `.dockerignore` (đặt ở gốc repo).
- `backend.Dockerfile`: base `python:3.12-slim`, copy `requirements.txt` cài trước (tận dụng layer cache), copy code, chạy `alembic upgrade head` (tự tạo schema DB nếu chưa có) rồi mới `uvicorn backend.main:app --host 0.0.0.0 --port 8000`. **Lưu ý**: image KHÔNG có `saved_models/*.pth` và `data/raw/` (gitignored) — bắt buộc mount volume, xem `docker-compose.yml`.
- `frontend.Dockerfile`: multi-stage — stage 1 `node:20-alpine` build `npm run build`, stage 2 `nginx:alpine` copy `dist/` + `nginx.conf`.
- `docker-compose.yml`: service `backend` (port 8000), `frontend` (port 80, phụ thuộc `backend`), volume mount `./saved_models`, `./data/raw`, và `./backend/db` (giữ DB SQLite qua các lần container restart) vào container backend.
- **⚠️ Frontend hiện hardcode gọi thẳng `http://localhost:8000`** (`frontend/src/api/axios.js`, `DashboardPage.jsx`) — CHƯA dùng đường dẫn tương đối qua `nginx.conf`'s reverse proxy `/api`/`/ws`. Vì vậy `docker-compose.yml` vẫn publish port 8000 ra host để code hiện tại chạy đúng không cần sửa. `nginx.conf` đã cấu hình sẵn proxy `/api`, `/ws` — khi Track A đổi frontend sang gọi đường dẫn tương đối (tiện thể lúc làm CP3.6 sửa URL WS), không cần sửa lại `nginx.conf`.
- **Phát hiện quan trọng lúc build — dọn `requirements.txt` (cả 2 loại lỗi này CHỈ lộ ra khi build container sạch, venv dev đã tích luỹ gói ngoài file này từ trước nên che mất cả 2 phía)**:
  1. *Thừa, chưa bao giờ dùng*: `tensorflow==2.20.0` + `keras==3.13.2` (620MB+) và `fastapi-cors` **chưa từng được import ở bất kỳ đâu trong code** (grep toàn repo, 0 kết quả — CORS thực tế chạy bằng `fastapi.middleware.cors.CORSMiddleware` có sẵn trong lõi FastAPI). Xoá cả 4 gói (`h5py`, `protobuf` ăn theo tensorflow cũng xoá luôn). `torch` không ghim rõ nguồn nên trên Linux pip mặc định tải kèm toàn bộ CUDA/GPU toolkit (nvidia-*, triton...) dù service chỉ chạy CPU — sửa `backend.Dockerfile` cài `torch` từ index CPU-only riêng (`--index-url https://download.pytorch.org/whl/cpu`) trước, giảm từ hàng GB xuống còn 191.8MB.
  2. *Thiếu, chưa từng khai báo*: `pydantic-settings` (`backend/core/config.py` luôn import nhưng chưa bao giờ có trong file) và `python-multipart` (FastAPI cần ngầm cho `UploadFile`/form-data ở `/api/diagnosis/upload-ecg`, chỉ báo lỗi đúng lúc route đó được đăng ký lúc khởi động, không có dòng `import` nào để rà bằng grep) — cả 2 đã thêm.
- **Phát hiện thêm lúc chạy thật**: `docker compose logs` ban đầu thiếu hẳn dòng banner khởi động + log nạp model — do container stdout không phải TTY nên Python mặc định block-buffering, giữ `print()` lại rất lâu thay vì flush ngay. Thêm `ENV PYTHONUNBUFFERED=1` vào `backend.Dockerfile` (đặt SAU các bước `pip install` nặng để không làm mất cache, không đặt ở đầu file) — xác nhận log hiện đủ ngay lập tức sau khi sửa.
- **DoD đã đạt**: `docker compose up -d --build` từ máy có sẵn `saved_models/` và `data/raw/` chạy đúng cả 2 container; xác nhận `MODEL READY: True` (model nạp thành công qua volume mount), `GET /api/records` trả đúng 48 bản ghi qua `curl http://localhost:8000/api/records`, log khởi động hiện đầy đủ ngay lập tức.

#### 6.4. CP 6.4 — CI/CD Pipeline (GitHub Actions) — ✅ Hoàn thành 2026-08-31
**File**: `.github/workflows/ci-cd.yml`, `ruff.toml` (mới).
- 5 job chạy trên mọi PR/push vào `main`: `lint-backend`, `lint-frontend`, `test-backend`, `test-frontend`, `build-docker` (phụ thuộc 4 job trước, chỉ chạy nếu tất cả pass).
- **`lint-backend`**: `ruff check backend/ src/ tests/`. Đã thử chạy ruff với rule mặc định trước khi đưa vào CI — phát hiện 104 lỗi, phần lớn là style thuần tuý (thứ tự import, `Optional[X]` vs `X | None`...) và **1 rule (`B008`) báo sai**: coi `Depends(...)` làm giá trị mặc định của FastAPI là anti-pattern, trong khi đó CHÍNH LÀ cách dùng chuẩn của framework. Giới hạn `ruff.toml` chỉ bật nhóm `F` (pyflakes: import/biến thật sự không dùng, lỗi cú pháp) — còn đúng 11 lỗi, đều là phát hiện thật (import thừa, tiền tố `f` thừa), đã tự sửa (`ruff check --fix`) để CI khởi động sạch, chạy lại toàn bộ 26 test xác nhận không có gì hỏng.
- **`lint-frontend`**: `npm run lint` (oxlint có sẵn từ trước) — hiện chỉ có warning (unused var, missing hook dep...), không có lỗi, không làm CI đỏ; đây là code Track A, không tự sửa.
- **`test-backend`**: cài `torch` từ index CPU-only trước `requirements.txt` (giống `backend.Dockerfile`, tránh kéo cả bộ CUDA trên Linux runner) rồi chạy `pytest tests/ -v` — các test cần `data/raw/`/`saved_models/`/ONNX tự skip qua marker đã có sẵn từ CP6.2, không cần sửa gì thêm.
- **`test-frontend`**: kiểm tra `package.json` có script `test` chưa (Track A chưa thêm Vitest) trước khi chạy — chưa có thì in thông báo bỏ qua thay vì làm CI đỏ vì lý do "chưa tới lượt", tự động chạy thật khi Track A thêm Vitest mà không cần sửa lại workflow.
- **`build-docker`**: build cả 2 Dockerfile, quét lỗ hổng bảo mật ảnh backend bằng `aquasecurity/trivy-action` (chỉ báo cáo, `exit-code: "0"` — không làm CI đỏ vì CVE của image nền ngoài tầm kiểm soát của repo; ghim `@master` thay vì 1 tag cụ thể vì không xác minh được tag chính xác lúc viết workflow, không có mạng truy cập GitHub), rồi chạy `docker compose up -d` thật + `curl` xác nhận cả 2 service phản hồi (không kiểm tra kết quả AI đúng/sai vì CI không có `saved_models/`/`data/raw/` thật — chỉ xác nhận container không crash).
- Đã thêm `ruff==0.16.5` vào `requirements.txt` (đồng bộ version với CI) theo đúng tiền lệ đã có với `pytest` ở CP6.2 (dự án không tách dev-requirements riêng).
- **DoD đã đạt**: cấu hình đầy đủ 5 job, đã kiểm chứng cục bộ từng phần (ruff sạch, oxlint sạch/chỉ warning, 26 test pytest xanh, YAML hợp lệ) — chưa kiểm chứng được bằng 1 lần chạy Actions thật (cần push lên GitHub mới thấy), nhưng mọi thành phần đã tự chạy đúng cục bộ với đúng lệnh workflow sẽ gọi.

#### 6.5. CP 6.5 — Hoàn thiện Tài liệu Kỹ thuật — 🟡 2/3 phần xong (2026-09-02), phần còn lại chờ Track A
- ✅ `docs/api_reference.md`: liệt kê đầy đủ mọi endpoint hiện có (WS `/ws/ecg`, `GET /api/records`, `POST /api/diagnosis/upload-ecg`, `POST/GET /api/auth/*`, `GET /api/anomalies`, `POST /api/anomalies/{id}/verify`) kèm request/response mẫu, mã lỗi, 3 tài khoản test.
- ✅ `docs/deployment_guide.md`: hướng dẫn cả 2 cách chạy (Docker Compose và thủ công), bảng biến môi trường override được, và mục riêng ghi lại **các lỗi thực tế đã gặp lúc làm CP6.3** (thiếu `pydantic-settings`/`python-multipart`, buffering log, torch kéo theo CUDA) kèm cách xử lý — tránh người sau lặp lại đúng những lỗi đã tốn công tìm ra.
- ✅ Cập nhật `README.md`: thêm link tới 2 file trên, thêm lựa chọn chạy bằng Docker Compose.
- ⏳ **Còn lại — cần Track A xong CP3.6/CP4 trước mới viết được**: hướng dẫn demo trực quan cho buổi bảo vệ đồ án (kịch bản click-through đủ tính năng frontend+backend).
- **DoD**: người ngoài dự án đọc `README.md` + `docs/deployment_guide.md` là chạy được toàn bộ hệ thống từ máy sạch — **đã đạt** cho phần backend/Docker; phần kịch bản demo đầy đủ tính năng chờ Track A.

#### 6.6. Sub-checkpoints
- [x] **CP 6.1** PyTorch → ONNX & Quantization Pipeline — Hoàn thành 2026-08-30
- [x] **CP 6.2** Automated Test Suite — phần backend (pytest) hoàn thành 2026-08-31, 26/26 test xanh; phần frontend (Vitest) là việc Track A
- [x] **CP 6.3** Dockerization — Hoàn thành 2026-08-31
- [x] **CP 6.4** CI/CD GitHub Actions Workflow — Hoàn thành 2026-08-31 (chờ lần push đầu để xác nhận chạy thật trên GitHub)
- [ ] **CP 6.5** Tài liệu Kỹ thuật & Deployment Guide — 2/3 xong (api_reference.md, deployment_guide.md), còn kịch bản demo chờ Track A

---

## IV. BẢNG TỔNG HỢP TIẾN ĐỘ

| Checkpoint | Hạng mục công việc | Trạng thái | Track phụ trách | Độ phức tạp |
|:---|:---|:---:|:---:|:---:|
| **CP 1** | Tiền xử lý dữ liệu MIT-BIH, SMOTE, 5 Models, Benchmark, Grad-CAM | ✅ 100% | — | Cao |
| **CP 2** | FastAPI WebSocket, Singleton Inference, React Plotly Dashboard, XAI Page | ✅ 100% | — | Trung bình |
| **CP 3** | DSP, Pan-Tompkins R-peak, BPM/HRV, record switcher, upload chẩn đoán | ✅ 100% (backend) | — | Trung bình |
| **CP 3.6** | Nối Frontend với API CP3 | ⏳ Chưa làm | Track A (Frontend) | Thấp |
| **CP 4** | Patient Management, Alarm System, Report Exporter, XAI Explainer, Settings | ⏳ Chưa làm | Track A (Frontend) | Trung bình |
| **CP 5** | Database, Auth JWT, RBAC, Human-in-the-loop | ✅ CP5.1-5.4 xong (backend) — 5.5 là việc Track A | Track B (Backend) | Cao |
| **CP 5.5** | Frontend Auth Guard | ⏳ Chưa làm | Track A (chờ CP5.2 hoặc mock) | Thấp |
| **CP 6** | ONNX, Test Suite, Docker, CI/CD, Docs | 🟡 CP6.1-6.4 xong, CP6.5 backend xong 2/3 — chỉ còn kịch bản demo chờ Track A | Track B (Backend) | Cao |

---

## V. ĐỀ XUẤT CÁC BƯỚC HÀNH ĐỘNG TIẾP THEO (NEXT STEPS)

1. ~~Đồng bộ hoá Git, merge về `main`~~ ✅ Xong.
2. ~~Vá lỗi lệch miền dữ liệu train/serving~~ ✅ Xong.
3. ~~Hoàn thiện Checkpoint 3 (backend)~~ ✅ Xong — Accuracy end-to-end 94.33%, không cần train lại model.
4. **Chia việc cho 2 người, bắt đầu Checkpoint 3.6 + 4 (Track A) và Checkpoint 5 + 6 (Track B) song song** — xem chi tiết phân công, thứ tự làm, và giao thức đồng bộ giữa 2 người tại **[pccv.md](pccv.md)**.
