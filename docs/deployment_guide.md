# Deployment Guide

Hướng dẫn chạy toàn bộ hệ thống (backend + frontend) — bằng Docker Compose (khuyến nghị)
hoặc thủ công không cần Docker. Chi tiết API xem [api_reference.md](api_reference.md), kiến
trúc tổng quan xem [architecture.md](architecture.md).

## 1. Chuẩn bị trước khi chạy (bắt buộc, cả 2 cách chạy)

`data/raw/`, `data/processed/`, `saved_models/*.pth` **không nằm trong git** (dung lượng lớn,
xem `.gitignore`) — không có 2 thứ này thì AI sẽ báo "Không tìm thấy model" và luồng WebSocket
không phát được tín hiệu, dù server vẫn khởi động "thành công" bình thường (không crash).

| Thứ cần có | Vị trí | Dung lượng | Bắt buộc? |
|---|---|---|---|
| Trọng số ResNet1D | `saved_models/resnet1d.pth` | 2.7MB | **Bắt buộc** — model production duy nhất |
| Bộ PhysioNet MIT-BIH (48 bản ghi) | `data/raw/physionet_mitdb/` | 90MB | **Bắt buộc** — nguồn tín hiệu stream demo |
| Bộ Kaggle CSV | `data/raw/kaggle_csv/` | 556MB | Không cần (chỉ dùng để tự huấn luyện lại model, xem `README.md`) |

Xin file trực tiếp từ người đã có sẵn (nhanh hơn nhiều so với tự tải+train lại), hoặc tự tái
tạo theo hướng dẫn trong `README.md` mục "Dữ liệu & trọng số model".

## 2. Chạy bằng Docker Compose (khuyến nghị)

Yêu cầu: đã cài Docker Desktop (hoặc Docker Engine + Compose plugin) và đã bật daemon.

```bash
docker compose up -d --build
```

Lần đầu build có thể mất khá lâu (tải `python:3.12-slim`, `node:20-alpine`, `nginx:alpine`,
và cài `torch` + các thư viện ML — xem mục 5 nếu build chậm bất thường). Các lần sau nhanh
hơn nhiều nhờ layer cache (chỉ rebuild lại phần đã đổi).

**Kiểm tra đã chạy đúng chưa**:
```bash
docker compose ps                        # cả 2 service phải "running"
docker compose logs backend --tail 30    # phải thấy dòng "AI Model & Grad-CAM đã sẵn sàng"
curl http://localhost:8000/api/records   # phải trả JSON danh sách 48 bản ghi
```
Mở `http://localhost` trên trình duyệt để xem Dashboard.

**Dừng lại**:
```bash
docker compose down
```
Dữ liệu SQLite (`backend/db/ecg_system.db`) được mount từ host nên **không mất** khi dừng/khởi
động lại container (khác với dữ liệu bên trong container mà không mount thì sẽ mất).

### Cấu trúc container

- `backend` (`backend.Dockerfile`): Python 3.12-slim + FastAPI + PyTorch (CPU-only). Chạy
  `alembic upgrade head` (tự tạo schema DB nếu chưa có) rồi mới khởi động `uvicorn`. Publish
  ra host port **8000**.
- `frontend` (`frontend.Dockerfile`): build 2 giai đoạn — Node 20 build React, rồi chỉ đóng
  gói file tĩnh vào Nginx (image cuối không có Node). Publish ra host port **80**.

**⚠️ Lưu ý**: frontend hiện tại (`frontend/src/api/axios.js`, `DashboardPage.jsx`) hardcode gọi
thẳng `http://localhost:8000` cho cả REST lẫn WebSocket — CHƯA đi qua reverse proxy `/api`,
`/ws` mà `nginx.conf` đã cấu hình sẵn. Vì vậy port 8000 của backend vẫn phải publish ra host
song song với port 80 của frontend. Khi frontend đổi sang gọi đường dẫn tương đối, không cần
sửa `nginx.conf` — chỉ cần sửa code frontend.

## 3. Biến môi trường có thể tuỳ chỉnh

Đọc từ `backend/core/config.py` (`pydantic-settings`, đọc biến môi trường theo đúng tên biến,
phân biệt hoa/thường).

- **Chạy thủ công (mục 4)**: export biến trước khi chạy `uvicorn` là có tác dụng ngay
  (`pydantic-settings` tự đọc biến môi trường của tiến trình).
- **Chạy bằng Docker Compose (mục 2)**: `docker-compose.yml` hiện **chưa** có mục `environment:`/`env_file:`
  cho service `backend` — chỉ tạo file `.env` ở gốc repo KHÔNG tự động bơm biến vào container.
  Muốn override thật, thêm 1 trong 2 cách vào `docker-compose.yml`:
  ```yaml
  services:
    backend:
      environment:
        - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      # hoac: env_file: .env
  ```
  rồi mới tạo file `.env` tương ứng — Docker Compose sẽ tự nạp `.env` ở gốc repo để thay thế
  `${...}` trong chính file `docker-compose.yml`, nhưng vẫn cần khai báo `environment:`/`env_file:`
  như trên thì giá trị đó mới thực sự vào được container.

| Biến | Mặc định | Ghi chú |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./backend/db/ecg_system.db` | Đổi sang PostgreSQL khi cần (vd `postgresql://user:pass@host/db`) mà không cần sửa code |
| `JWT_SECRET_KEY` | 1 chuỗi cố định chỉ dùng dev | **Bắt buộc đổi** trước khi triển khai ngoài máy cá nhân — đổi secret chỉ làm mọi token cũ hết hiệu lực, không có tác dụng phụ nguy hiểm nào khác |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:5173", "http://127.0.0.1:5173"]` | Thêm origin của frontend thật nếu khác 2 địa chỉ dev mặc định |

## 4. Chạy thủ công, không dùng Docker (dev hàng ngày)

```bash
python -m venv venv
venv/Scripts/activate        # Windows — Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head          # tạo schema DB lần đầu (giống bước Docker tự làm)
python -m backend.scripts.seed_users    # tạo 3 tài khoản test (tuỳ chọn)
uvicorn backend.main:app --reload --port 8000
```
Frontend (terminal khác):
```bash
cd frontend
npm install
npm run dev
```
Frontend chạy tại `http://localhost:5173`, gọi thẳng backend tại `http://localhost:8000`
(không qua Nginx — chỉ Docker Compose mới có Nginx).

## 5. Các vấn đề đã gặp thực tế khi làm CP6.3 & cách xử lý

Ghi lại để không ai mất công tìm lại lần nữa nếu gặp đúng những lỗi này:

- **`ModuleNotFoundError: No module named 'pydantic_settings'` hoặc tương tự khi container
  khởi động** dù `pip install -r requirements.txt` "chạy được" trên máy dev: venv dev có thể
  đã tích luỹ gói cài ngoài `requirements.txt` (cài tay từ trước, không ai để ý) — chỉ lộ ra
  khi build container THẬT SẠCH. Đã xảy ra với `pydantic-settings` và `python-multipart`
  (FastAPI cần ngầm cho `UploadFile`, chỉ báo lỗi đúng lúc route liên quan được đăng ký).
  Nếu gặp lỗi thiếu module tương tự: thêm đúng gói đó vào `requirements.txt`, đừng chỉ cài tay
  trên máy — sẽ lại mất công y hệt ở máy/container tiếp theo.
- **`docker compose logs backend` không hiện gì dù server có vẻ chạy được** (thiếu cả dòng
  banner khởi động lẫn log nạp model): container's stdout không phải TTY nên Python mặc định
  block-buffering, giữ `print()` lại rất lâu thay vì flush ngay. Đã sửa bằng
  `ENV PYTHONUNBUFFERED=1` trong `backend.Dockerfile` — nếu tự viết Dockerfile Python khác,
  nhớ thêm dòng này (đặt SAU các bước `pip install` nặng, không phải đầu file, để không làm
  mất cache của các bước đó khi rebuild).
- **Build backend rất chậm / tải hàng GB không rõ lý do**: `torch` không ghim rõ nguồn cài thì
  trên Linux, pip mặc định tải kèm toàn bộ CUDA/GPU toolkit (`nvidia-*`, `triton`...) dù service
  chỉ chạy CPU. Đã sửa bằng cách cài `torch` từ index CPU-only riêng
  (`pip install torch --index-url https://download.pytorch.org/whl/cpu`) **trước** khi
  `pip install -r requirements.txt` — giảm từ hàng GB xuống còn ~192MB.
- **Model báo "Không tìm thấy model" dù `saved_models/resnet1d.pth` có thật trên host**: kiểm
  tra volume mount đúng đường dẫn tương đối (`./saved_models:/app/saved_models`, khớp
  `WORKDIR /app` trong `backend.Dockerfile`) và đường dẫn tương đối trong code
  (`os.path.join("saved_models", "resnet1d.pth")`) — 2 bên phải khớp nhau về gốc.

## 6. Kiểm thử tự động trước khi deploy

```bash
python -m ruff check backend/ src/ tests/    # lint (CI cũng chạy đúng lệnh này)
python -m pytest tests/ -v                    # 26 test, tự skip phần cần data/raw/ hoặc saved_models/
cd frontend && npm run lint                   # oxlint
```
CI/CD đầy đủ (lint + test + build Docker + quét lỗ hổng bảo mật) chạy tự động trên mọi PR/push
vào `main` — xem `.github/workflows/ci-cd.yml`.
