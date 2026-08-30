from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Thông tin dự án
    PROJECT_NAME: str = "ECG Real-time Backend"
    PROJECT_VERSION: str = "1.0.0"
    
    # Cấu hình mạng & CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Đường dẫn file dữ liệu
    MOCK_DATA_PATH: str = "data/mock_ecg.csv"

    # Cấu hình Database (CP5.1) — SQLite cho giai đoạn dev, đổi qua biến môi trường
    # DATABASE_URL khi cần chuyển sang PostgreSQL (CP6.3 Docker) mà không sửa code.
    DATABASE_URL: str = "sqlite:///./backend/db/ecg_system.db"

    class Config:
        case_sensitive = True

# Khởi tạo đối tượng settings để các file khác import dùng chung
settings = Settings()