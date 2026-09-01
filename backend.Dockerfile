# CP6.3: Image Backend (FastAPI + PyTorch inference + SQLite/Alembic).
# saved_models/ va data/raw/ KHONG nam trong image (gitignored, qua lon de bake) -
# duoc mount qua volume trong docker-compose.yml, phai co san o host truoc khi "docker compose up".
FROM python:3.12-slim

WORKDIR /app

# Cai dependency truoc, tach rieng khoi COPY code de tan dung layer cache cua Docker:
# chi rebuild lai buoc pip install khi requirements.txt thay doi, khong phai moi lan sua code.
#
# QUAN TRONG: cai torch tu index rieng cho ban CPU-only truoc. Neu de pip tu chon (khong chi
# dinh index), tren Linux no mac dinh ke ca "cuda-toolkit"/"nvidia-*"/"triton" (hang GB, dung
# cho GPU) du service nay chi chay CPU (ResNet1D o day nho, khong can GPU) - lam image nang len
# rat nhieu va build cham han. Da phat hien thuc te khi build lan dau: rieng tensorflow+torch(CUDA)
# keo dai vai tram MB~vai GB tai ve khong can thiet.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY src/ src/
COPY data/preprocess.py data/preprocess.py
COPY alembic.ini .

EXPOSE 8000

# Chay migration DB (tao du bang neu chua co) truoc khi khoi dong server, dam bao schema
# luon dung moi lan container khoi dong - xem backend/db/migrations/.
CMD alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000
