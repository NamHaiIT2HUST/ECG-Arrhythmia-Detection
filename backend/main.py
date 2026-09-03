from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.ws_routes import router as ws_router
from backend.api.records_routes import router as records_router
from backend.api.diagnosis_routes import router as diagnosis_router
from backend.api.auth import router as auth_router
from backend.api.anomalies import router as anomalies_router
from backend.core.config import settings
from backend.service.inference_service import ai_service
import os
from backend.db.session import engine
from backend.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi động (Startup)
    print("===========================================")
    print("🚀 BẮT ĐẦU KHỞI ĐỘNG HỆ THỐNG ECG BACKEND 🚀")
    print("===========================================")
    
    # Nạp model ResNet1D vào RAM
    model_path = os.path.join("saved_models", "resnet1d.pth")
    ai_service.load_model(model_path)

    # Ensure DB tables exist for development/demo (create missing tables).
    # Import models so they are registered on Base.metadata before create_all
    try:
        import backend.db.models  # noqa: F401 (register models)
        Base.metadata.create_all(bind=engine)
        print('[DB] Đã kiểm tra/khởi tạo schema (nếu cần).')
    except Exception as e:
        print(f"[DB] Không thể tạo bảng: {e}")
    
    yield
    
    # Tắt máy (Shutdown)
    print("===========================================")
    print("🛑 HỆ THỐNG ĐÃ TẮT 🛑")
    print("===========================================")

# Khởi tạo app dùng thông số từ thư mục core
app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan)

# Cấu hình CORS lấy từ settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Trái tim hệ thống ECG đang đập bình thường! 💓",
        "websocket_endpoint": "ws://localhost:8000/ws/ecg",
        "status": "online"
    }

# Gắn Router
app.include_router(ws_router)
app.include_router(records_router)
app.include_router(diagnosis_router)
app.include_router(auth_router)
app.include_router(anomalies_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)