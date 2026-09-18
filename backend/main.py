from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.ws_routes import router as ws_router
from backend.api.records_routes import router as records_router
from backend.api.diagnosis_routes import router as diagnosis_router
from backend.api.afib_routes import router as afib_router
from backend.api.auth import router as auth_router
from backend.api.anomalies import router as anomalies_router
from backend.api.admin_routes import router as admin_router
from backend.core.config import settings, DEFAULT_JWT_SECRET_KEY
from backend.service.inference_service import ai_service
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("===========================================")
    print("🚀 BẮT ĐẦU KHỞI ĐỘNG HỆ THỐNG ECG BACKEND 🚀")
    print("===========================================")

    if settings.JWT_SECRET_KEY == DEFAULT_JWT_SECRET_KEY:
        print("⚠️  [CẢNH BÁO BẢO MẬT] JWT_SECRET_KEY đang dùng giá trị mặc định (dev-only, "
              "công khai trong source code) - ai đọc được repo đều có thể tự ký token giả mạo "
              "bất kỳ quyền nào. Đặt biến môi trường JWT_SECRET_KEY thật trước khi triển khai "
              "ngoài máy cá nhân, xem docs/deployment_guide.md.")

    model_path = os.path.join("saved_models", "resnet1d.pth")
    ai_service.load_model(model_path)

    yield
    
    print("===========================================")
    print("🛑 HỆ THỐNG ĐÃ TẮT 🛑")
    print("===========================================")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan)

# Add Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

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

app.include_router(ws_router)
app.include_router(records_router)
app.include_router(diagnosis_router)
app.include_router(afib_router)
app.include_router(auth_router)
app.include_router(anomalies_router)
app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

