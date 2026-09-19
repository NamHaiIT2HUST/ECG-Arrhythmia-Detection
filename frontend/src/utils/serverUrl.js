// Xác định địa chỉ backend cho cả REST (axios) và WebSocket - dùng CHUNG 1 chỗ để 2 kênh
// không bao giờ lệch nhau.
//
// Mặc định (wsUrlSetting rỗng): dùng CÙNG origin với trang web đang mở (qua nginx reverse
// proxy /api, /ws -> backend, xem nginx.conf) - nghĩa là bất kỳ ai mở trang từ máy nào cũng
// tự động gọi đúng backend đang phục vụ trang đó, không cần tự sửa gì. Trước đây mặc định
// hardcode "http://localhost:8000"/"ws://localhost:8000" - chỉ đúng trên đúng máy đang chạy
// backend; máy khác mở trang sẽ luôn gọi vào "localhost" của chính máy đó (rỗng/lỗi), và tệ
// hơn nữa: ô cấu hình để đổi việc này (Cài Đặt Hệ Thống) lại bị ẩn với mọi role trừ admin.
//
// Chỉ dùng `wsUrlSetting` (giá trị admin tự nhập ở Cài Đặt Hệ Thống) khi cần trỏ frontend
// sang 1 backend KHÁC origin hiện tại (vd debug frontend dev cục bộ với backend trên server
// khác) - trường hợp thông thường (deploy qua Docker Compose/nginx) để trống là đúng.
export const resolveWsBase = (wsUrlSetting) => {
  if (wsUrlSetting) return wsUrlSetting;
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}`;
};

export const resolveHttpBase = (wsUrlSetting) => {
  if (wsUrlSetting) return wsUrlSetting.replace(/^ws:/, 'http:').replace(/^wss:/, 'https:');
  // baseURL rỗng = axios tự ghép request với origin hiện tại của trang (relative).
  return '';
};
