# Tài liệu Frontend (Dashboard)

Hệ thống Dashboard được xây dựng bằng **React** (với Vite) nhằm cung cấp giao diện người dùng trực quan, hỗ trợ theo dõi tín hiệu ECG và hiển thị kết quả phân tích thời gian thực.

## 1. Công nghệ sử dụng

- **Framework:** [React](https://react.dev/) (phiên bản 18+) với [Vite](https://vite.dev/) làm công cụ xây dựng (build tool).
- **Biểu đồ:** [react-plotly.js](https://plotly.com/javascript/react/) - Thư viện chuyên dụng để vẽ tín hiệu ECG, hỗ trợ tương tác và phóng to/thu nhỏ.
- **Giao tiếp API:** [Axios](https://axios-http.com/) để gọi API từ Backend và [Socket.io-client](https://socket.io/) để lắng nghe dữ liệu ECG Real-time qua WebSocket.
- **Quản lý trạng thái:** React Hooks (`useState`, `useEffect`).

## 2. Hướng dẫn cài đặt

Để khởi chạy giao diện, đảm bảo bạn đã cài đặt [Node.js (LTS)](https://nodejs.org/).

### Bước 1: Di chuyển vào thư mục frontend

```bash
cd frontend
```

### Bước 2: Cài đặt các gói phụ thuộc

```bash
npm install
```

### Bước 3: Khởi chạy môi trường phát triển

```bash
npm run dev
```

Sau khi chạy, giao diện sẽ được truy cập tại:

```
http://localhost:5173
```

## 3. Cấu trúc thư mục Frontend

```text
frontend/
└── src/
    ├── api/             # Cấu hình axios để gọi backend
    ├── components/      # Các thành phần UI (ECGChart, AlarmWidget,...)
    ├── hooks/           # Các custom hooks (useWebSocket,...)
    ├── App.jsx          # File quản lý route và logic chính
    └── main.jsx         # Entry point của React
```