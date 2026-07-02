# Tài liệu Backend (FastAPI)

Backend được xây dựng để cung cấp API xử lý tín hiệu ECG và thực hiện dự đoán thời gian thực.

## 1. Cấu trúc thư mục
- api/: Chứa các endpoint (đường dẫn API).
- core/: Chứa các module xử lý tín hiệu ECG (lọc nhiễu, chuẩn hóa).
- service/: Chứa module load mô hình AI và thực hiện dự đoán.
- main.py: File khởi chạy ứng dụng FastAPI.

## 2. Công nghệ dự kiến
- Framework: FastAPI.
- Xử lý tín hiệu: Scipy, Numpy.
- AI/ML: Tensorflow.

## 3. Quy trình cài đặt
1. Kích hoạt venv.
2. Cài đặt thư viện: pip install -r requirements.txt.
3. Khởi chạy: uvicorn backend.main:app --reload.
