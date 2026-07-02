from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Thông tin dự án
    PROJECT_NAME: str = "ECG Real-time Backend"
    PROJECT_VERSION: str = "1.0.0"
    
    # Cấu hình mạng & CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Đường dẫn file dữ liệu
    MOCK_DATA_PATH: str = "data/mock_ecg.csv"
    
    class Config:
        case_sensitive = True

# Khởi tạo đối tượng settings để các file khác import dùng chung
settings = Settings()