# Tài liệu Frontend (Dashboard)

Hệ thống Dashboard được xây dựng bằng **React** (với Vite) nhằm cung cấp giao diện người dùng trực quan, hỗ trợ theo dõi tín hiệu ECG và hiển thị kết quả phân tích thời gian thực. Trải qua quá trình tái cấu trúc, mã nguồn hiện tại đã đạt chuẩn Modular và tích hợp nhiều tính năng của hệ thống Enterprise (Web Hệ thống Y tế).

## 1. Công nghệ sử dụng

- **Framework:** [React](https://react.dev/) (phiên bản 18+) với [Vite](https://vite.dev/) làm công cụ xây dựng (build tool).
- **Biểu đồ:** [react-plotly.js](https://plotly.com/javascript/react/) - Thư viện chuyên dụng để vẽ tín hiệu ECG, hỗ trợ tương tác và phóng to/thu nhỏ.
- **Giao tiếp API & Real-time:** 
  - [Axios](https://axios-http.com/) để gọi API RESTful từ Backend.
  - **Native WebSocket API** (`ws://...`) để giao tiếp thời gian thực với FastAPI, giúp stream luồng điện tâm đồ với độ trễ thấp nhất.
- **Quản lý trạng thái:** 
  - Sử dụng React Hooks (`useState`, `useEffect`).
  - Bổ sung **LocalStorage** để duy trì trạng thái lưu trữ thông tin bệnh nhân (Patient Profile) độc lập ở client.

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

Dự án áp dụng kiến trúc chuẩn Modular phân tách trách nhiệm rõ ràng, dễ bảo trì và tối ưu khả năng mở rộng:

```text
frontend/
└── src/
    ├── components/
    │   ├── layout/         # Sidebar.jsx, Header.jsx (Khung giao diện chính)
    │   └── dashboard/      # ECGChart.jsx, PatientInfo.jsx, EventLog.jsx, StatCards.jsx, LoadingSpinner.jsx
    ├── pages/              # DashboardPage.jsx (Lắp ráp các component lại thành trang hoàn chỉnh)
    ├── App.jsx             # Entry point định tuyến gọi DashboardPage
    ├── main.jsx            # Khởi tạo React DOM
    └── index.css           # Cấu hình CSS Global, Animation, Reset margin
```

## 4. Các tính năng nổi bật (Enterprise Features)

Giao diện đã được nâng cấp mạnh mẽ với 4 nhóm tính năng nghiệp vụ cốt lõi, nâng tầm ứng dụng lên chuẩn Y tế chuyên nghiệp:

- **Resilience & Auto-Reconnect:** Hệ thống có khả năng tự động phát hiện mất kết nối WebSocket và thử kết nối lại sau mỗi 3 giây. Giao diện thay đổi trạng thái UI một cách linh hoạt (cảnh báo "Đang kết nối lại...") nhằm duy trì nhận thức của người dùng về tình trạng hệ thống.
- **Explainable AI (XAI) UI:** Biểu đồ Plotly có khả năng highlight (tô màu vùng đỏ) trực tiếp lên dải sóng ECG ngay khi nhận được cảnh báo bất thường từ mô hình AI. Điều này cung cấp khả năng giải thích trực quan, hỗ trợ bác sĩ chẩn đoán chính xác vị trí phát sinh sự cố.
- **Patient Data Persistence:** Form hồ sơ bệnh nhân hỗ trợ nhập liệu kết hợp cơ chế tự động lưu và phục hồi trạng thái thông qua `LocalStorage`. Dữ liệu được bảo toàn liền mạch, chống thất thoát ngay cả khi người dùng làm mới (F5) trang web.
- **Dynamic Loading States:** Hiển thị vòng xoay chờ (Loading Spinner) thông minh khi đang thiết lập luồng dữ liệu lần đầu. Tính năng này giúp loại bỏ hoàn toàn hiện tượng màn hình trắng (White Screen of Death), tạo cảm giác ổn định, đáng tin cậy.