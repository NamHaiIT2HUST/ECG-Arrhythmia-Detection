import axios from 'axios';

// Derive REST base URL from saved settings (wsUrl) when possible.
// If user configured wsUrl like `ws://localhost:8000`, convert to `http://localhost:8000`.
const getDefaultBase = () => {
  try {
    const raw = localStorage.getItem('ecg_settings');
    if (!raw) return 'http://localhost:8000';
    const settings = JSON.parse(raw);
    if (settings.wsUrl) {
      return settings.wsUrl.replace(/^ws:/, 'http:').replace(/^wss:/, 'https:');
    }
  } catch (e) {
    // ignore
  }
  return 'http://localhost:8000';
};

const api = axios.create({
  baseURL: getDefaultBase(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;