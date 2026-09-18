import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import api from "../api/axios";
import { stopAlarm } from "../utils/alarmAudio";

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

const USER_CACHE_KEY = "ecg_auth_user";

const clearAuthStorage = () => {
  localStorage.removeItem(USER_CACHE_KEY);
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
  const [authLoading, setAuthLoading] = useState(true);

  const logout = async () => {
    try {
      await api.post("/api/auth/logout");
    } catch (e) {
      console.error("Logout error", e);
    }
    clearAuthStorage();
    setUser(null);
    stopAlarm();
  };

  const loggingOutRef = useRef(false);

  useEffect(() => {
    const resId = api.interceptors.response.use(
      (res) => res,
      async (error) => {
        const original = error.config;
        const isNonRetryableAuthEndpoint = original?.url === "/api/auth/login" || original?.url === "/api/auth/refresh";
        
        if (error.response?.status === 401 && original && !original._retry && !isNonRetryableAuthEndpoint) {
          original._retry = true;
          try {
            // Cookie contains refresh_token, backend will use it
            await api.post("/api/auth/refresh");
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
      api.interceptors.response.eject(resId);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const verify = async () => {
      try {
        const res = await api.get("/api/auth/me");
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
    await api.post("/api/auth/login", { username, password });
    loggingOutRef.current = false;
    const me = await api.get("/api/auth/me");
    setUser(me.data);
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(me.data));
    return me.data;
  };

  const getWsTicket = async () => {
    const res = await api.post("/api/auth/ws-ticket");
    return res.data.ticket;
  };

  const value = {
    user,
    login,
    logout,
    getWsTicket,
    authLoading,
    isAuthenticated: !!user,
    isAdmin: user?.role === "admin",
    isDoctor: user?.role === "doctor",
    isNurse: user?.role === "nurse",
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;

