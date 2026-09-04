import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import api from '../api/axios';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

const ACCESS_TOKEN_KEY = 'ecg_access_token';
const REFRESH_TOKEN_KEY = 'ecg_refresh_token';
const USER_CACHE_KEY = 'ecg_auth_user';

const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY);
const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY);

const setTokens = ({ access_token, refresh_token }) => {
  if (access_token) localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
};

const clearAuthStorage = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_CACHE_KEY);
};

// Gọi thẳng POST /api/auth/refresh (không qua interceptor bên dưới để tránh đệ quy).
const refreshAccessToken = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) throw new Error('Không có refresh token');
  const res = await api.post('/api/auth/refresh', { refresh_token: refreshToken });
  setTokens({ access_token: res.data.access_token });
  return res.data.access_token;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem(USER_CACHE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  // true trong lúc xác thực token đã lưu (nếu có) lúc mở app - tránh chớp LoginPage
  // rồi lại chớp về dashboard ngay sau đó khi token thực ra vẫn còn hợp lệ.
  const [authLoading, setAuthLoading] = useState(true);

  const logout = () => {
    clearAuthStorage();
    setUser(null);
  };

  // Đăng ký interceptor axios đúng 1 lần: tự đính Bearer token vào mọi request, và tự thử
  // refresh access token đúng 1 lần khi gặp 401 trước khi đá người dùng về LoginPage
  // (đúng hành vi đã ghi trong plan.md mục 5.3: "Frontend nên tự gọi /api/auth/refresh...").
  const loggingOutRef = useRef(false);
  useEffect(() => {
    const reqId = api.interceptors.request.use((config) => {
      const token = getAccessToken();
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    const resId = api.interceptors.response.use(
      (res) => res,
      async (error) => {
        const original = error.config;
        // Chỉ loại trừ chính /login và /refresh (retry 2 endpoint này sẽ vô nghĩa/lặp vô hạn).
        // /api/auth/me PHẢI được retry bình thường - đây chính là request verify() gọi lúc mở
        // app, và access token hết hạn sau 30 phút là tình huống rất thường gặp cần refresh.
        const isNonRetryableAuthEndpoint = original?.url === '/api/auth/login' || original?.url === '/api/auth/refresh';
        if (error.response?.status === 401 && original && !original._retry && !isNonRetryableAuthEndpoint && getRefreshToken()) {
          original._retry = true;
          try {
            const newToken = await refreshAccessToken();
            original.headers.Authorization = `Bearer ${newToken}`;
            return api.request(original);
          } catch {
            if (!loggingOutRef.current) {
              loggingOutRef.current = true;
              clearAuthStorage();
              setUser(null);
            }
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.request.eject(reqId);
      api.interceptors.response.eject(resId);
    };
  }, []);

  // Lúc mở app: nếu có token đã lưu, xác thực lại với GET /api/auth/me (nguồn sự thật duy
  // nhất cho role - không tin vào bản cache) trước khi coi là đã đăng nhập thật.
  useEffect(() => {
    let cancelled = false;
    const verify = async () => {
      if (!getAccessToken()) {
        setAuthLoading(false);
        return;
      }
      try {
        const res = await api.get('/api/auth/me');
        if (cancelled) return;
        setUser(res.data);
        localStorage.setItem(USER_CACHE_KEY, JSON.stringify(res.data));
      } catch {
        if (!cancelled) {
          clearAuthStorage();
          setUser(null);
        }
      } finally {
        if (!cancelled) setAuthLoading(false);
      }
    };
    verify();
    return () => { cancelled = true; };
  }, []);

  const login = async (username, password) => {
    const res = await api.post('/api/auth/login', { username, password });
    setTokens(res.data);
    loggingOutRef.current = false;
    const me = await api.get('/api/auth/me');
    setUser(me.data);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(me.data));
    return me.data;
  };

  const value = {
    user,
    login,
    logout,
    authLoading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isDoctor: user?.role === 'doctor',
    isNurse: user?.role === 'nurse',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
