import axios from 'axios';
import { resolveHttpBase } from '../utils/serverUrl';

// Suy ra REST base URL từ settings đã lưu (wsUrl) nếu admin đã cấu hình riêng; mặc định dùng
// cùng origin với trang web đang mở (xem utils/serverUrl.js để biết lý do đổi từ hardcode
// "http://localhost:8000" trước đây - vốn khiến máy khác mở trang không gọi được backend).
const getDefaultBase = () => {
  try {
    const raw = localStorage.getItem('ecg_settings');
    const settings = raw ? JSON.parse(raw) : {};
    return resolveHttpBase(settings.wsUrl);
  } catch (e) {
    return resolveHttpBase(null);
  }
};

const api = axios.create({
  baseURL: getDefaultBase(),
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;