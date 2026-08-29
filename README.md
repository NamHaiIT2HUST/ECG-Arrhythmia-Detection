# ECG Arrhythmia Detection & Explainable AI

Hệ thống giám sát điện tâm đồ (ECG) thời gian thực, phát hiện rối loạn nhịp tim bằng Deep Learning (PyTorch) và giải thích quyết định của mô hình bằng 1D Grad-CAM. Backend FastAPI stream tín hiệu qua WebSocket, frontend React 19 + Plotly hiển thị dashboard theo thời gian thực.

> Tài liệu kế hoạch phát triển chi tiết (checkpoint, lộ trình, đánh giá hiện trạng): xem [plan.md](plan.md).
> Tài liệu chuyên sâu từng phần: xem thư mục [docs/](docs/).

## Kiến trúc tổng quan

```
data/         Tiền xử lý dữ liệu MIT-BIH (Kaggle CSV + PhysioNet WFDB), SMOTE, xuất .npy
src/          Kiến trúc 5 model 1D (ResNet1D, CNN-LSTM, TCN, Transformer1D, Mamba1D) + benchmark + Grad-CAM
backend/      FastAPI + WebSocket streaming, inference service (singleton), tiền xử lý tín hiệu
frontend/     React 19 + Vite + Plotly dashboard real-time, trang phân tích XAI
saved_models/ Trọng số các model đã train (.pth, không commit vào git — xem hướng dẫn bên dưới)
```

Chi tiết luồng dữ liệu: [docs/architecture.md](docs/architecture.md).

## Model production

Model đang được dùng để inference là **ResNet1D**, chọn theo kết quả benchmark 5 kiến trúc trên tập test Kaggle MIT-BIH (5 lớp AAMI: N/S/V/F/Q):

| Model | Accuracy | F1-Score (macro) | Latency |
|---|---|---|---|
| **ResNet1D** | **98.57%** | **92.16%** | 0.13 ms |
| CNN1D_LSTM | 97.27% | 85.79% | 0.18 ms |
| TCN | 96.17% | 82.81% | 0.79 ms |
| Transformer1D | 95.36% | 83.11% | 0.43 ms |
| Mamba1D | 94.45% | 79.28% | 0.47 ms |

Bảng đầy đủ + cách tái tạo: [docs/benchmark_results.md](docs/benchmark_results.md), [docs/data_preprocessing.md](docs/data_preprocessing.md).

## Cài đặt

```bash
python -m venv venv
venv/Scripts/activate        # Windows
pip install -r requirements.txt
cd frontend && npm install
```

### Dữ liệu & trọng số model

`data/raw/`, `data/processed/` và `saved_models/*.pth` không được commit vào git (dữ liệu lớn, xem `.gitignore`). Để chạy được hệ thống từ máy sạch:

1. Tải MIT-BIH Arrhythmia Database (bản Kaggle CSV và/hoặc bản PhysioNet WFDB gốc) vào `data/raw/kaggle_csv/` và `data/raw/physionet_mitdb/`.
2. Tiền xử lý dữ liệu: `python data/preprocess.py`
3. Train & benchmark toàn bộ 5 model (tự động lưu `.pth` vào `saved_models/`):
   ```bash
   python src/benchmark.py
   ```

## Chạy hệ thống

```bash
# Backend (từ thư mục gốc repo)
uvicorn backend.main:app --reload --port 8000

# Frontend (thư mục frontend/)
npm run dev
```

Backend mặc định stream bản ghi PhysioNet record 208 (nhiều PVC) qua `ws://localhost:8000/ws/ecg`. Frontend chạy tại `http://localhost:5173`.

### API chính

- `WS /ws/ecg?record=<id>` — stream real-time (mặc định `record=208`). Mỗi gói tin gồm `chunk` (10 điểm vẽ biểu đồ), `prediction`/`heatmap`/`latency_ms` (giữ nguyên giữa 2 nhịp, chỉ cập nhật khi `is_new_beat=true`), `bpm`, `hrv_sdnn`, `hrv_rmssd`.
- `GET /api/records` — danh sách bản ghi PhysioNet khả dụng kèm mô tả lâm sàng, dùng để đổ vào dropdown chọn bản ghi.
- `POST /api/diagnosis/upload-ecg?fs=360` — upload file CSV 1 cột tín hiệu ECG, trả về báo cáo chẩn đoán offline (phân bố lớp AAMI, BPM, HRV, danh sách nhịp bất thường).

### Kiểm thử pipeline AI

```bash
python -m backend.scripts.validate_qrs             # độ chính xác phát hiện đỉnh R so với nhãn bác sĩ (F1)
python -m backend.scripts.validate_classification   # độ chính xác chẩn đoán end-to-end (raw signal -> AAMI)
python -m backend.scripts.test_ws [record_id]        # xem thử payload WebSocket thực tế
```

## Trạng thái & hướng phát triển

Xem [plan.md](plan.md) để biết checkpoint nào đã hoàn thành, checkpoint nào đang làm tiếp theo (DSP nâng cao, R-peak detection động, quản lý bệnh nhân, database/auth, Docker/CI-CD...).
