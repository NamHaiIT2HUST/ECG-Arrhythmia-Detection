from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Thông tin dự án
    PROJECT_NAME: str = "ECG Real-time Backend"
    PROJECT_VERSION: str = "1.0.0"
    
    # Cấu hình mạng & CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ]
    
    # Đường dẫn file dữ liệu
    MOCK_DATA_PATH: str = "data/mock_ecg.csv"

    # Cấu hình Database (CP5.1) — SQLite cho giai đoạn dev, đổi qua biến môi trường
    # DATABASE_URL khi cần chuyển sang PostgreSQL (CP6.3 Docker) mà không sửa code.
    DATABASE_URL: str = "sqlite:///./backend/db/ecg_system.db"

    # Cấu hình JWT (CP5.2). ⚠️ JWT_SECRET_KEY mặc định CHỈ dùng cho dev/demo local —
    # bắt buộc override bằng biến môi trường JWT_SECRET_KEY thật trước khi triển khai
    # ngoài máy cá nhân (đổi secret sẽ làm mọi token cũ hết hiệu lực, không có tác dụng phụ nguy hiểm).
    JWT_SECRET_KEY: str = "dev-only-doi-bien-moi-truong-truoc-khi-trien-khai-that-8f3a1c9e2b7d"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(case_sensitive=True)

# Khởi tạo đối tượng settings để các file khác import dùng chung
settings = Settings()