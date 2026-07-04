from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.ws_routes import router as ws_router
from core.config import settings

# Khởi tạo app dùng thông số từ thư mục core
app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Cấu hình CORS lấy từ settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn Router
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)