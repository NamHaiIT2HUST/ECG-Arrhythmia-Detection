import React, { createContext, useState, useContext, useEffect } from 'react';

const AnomalyContext = createContext();

export const useAnomaly = () => useContext(AnomalyContext);

const ANOMALY_STORAGE_KEY = 'ecg_anomaly_history';

export const AnomalyProvider = ({ children }) => {
  // Lưu trữ lịch sử các nhịp tim lỗi - nạp từ localStorage để không bị mất khi F5 hoặc chuyển tab
  const [anomalyHistory, setAnomalyHistory] = useState(() => {
    try {
      const raw = localStorage.getItem(ANOMALY_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });
  
  // Lưu nhịp tim đang được xem chi tiết
  const [selectedAnomaly, setSelectedAnomaly] = useState(() => {
    try {
      const raw = localStorage.getItem(ANOMALY_STORAGE_KEY);
      const list = raw ? JSON.parse(raw) : [];
      return list.length > 0 ? list[0] : null;
    } catch {
      return null;
    }
  });

  // Tự động lưu anomalyHistory vào localStorage khi có thay đổi
  useEffect(() => {
    try {
      localStorage.setItem(ANOMALY_STORAGE_KEY, JSON.stringify(anomalyHistory));
    } catch (e) {
      console.error('Failed save anomaly history to localStorage', e);
    }
  }, [anomalyHistory]);

  // Tự động chọn nhịp đầu tiên nếu chưa chọn nhịp nào
  useEffect(() => {
    if (!selectedAnomaly && anomalyHistory.length > 0) {
      setSelectedAnomaly(anomalyHistory[0]);
    }
  }, [selectedAnomaly, anomalyHistory]);

  const addAnomaly = (anomalyData) => {
    setAnomalyHistory(prev => {
      // Tránh duplicate: nếu cùng anomalyId từ DB hoặc 2 gói trùng nhau quá sát (< 350ms)
      const last = prev[0];
      if (last) {
        if (anomalyData.anomalyId && last.anomalyId && last.anomalyId === anomalyData.anomalyId) {
          return prev;
        }
        if (Date.now() - last.timestamp < 350) {
          return prev;
        }
      }
      
      const newAnomaly = {
        ...anomalyData,
        id: anomalyData.anomalyId || Date.now(),
        timestamp: Date.now(),
        time: new Date().toLocaleTimeString('vi-VN'),
      };
      
      const newHistory = [newAnomaly, ...prev].slice(0, 30); // Giữ 30 lỗi gần nhất
      
      setSelectedAnomaly(prevSelected => prevSelected || newAnomaly);
      
      return newHistory;
    });
  };

  // CP5.4: dùng sau khi bác sĩ xác nhận/sửa nhãn AI (XAIPage) - cập nhật đồng thời cả item
  // trong danh sách lịch sử VÀ bản đang xem chi tiết (2 object khác nhau sau addAnomaly, nếu
  // chỉ sửa 1 bên sẽ lệch trạng thái giữa list và khung chi tiết).
  const updateAnomaly = (id, patch) => {
    setAnomalyHistory(prev => prev.map(item => (item.id === id || item.anomalyId === id ? { ...item, ...patch } : item)));
    setSelectedAnomaly(prev => (prev && (prev.id === id || prev.anomalyId === id) ? { ...prev, ...patch } : prev));
  };

  // Gọi khi đổi bệnh nhân/bản ghi đang theo dõi (MonitoringContext)
  const clearHistory = () => {
    setAnomalyHistory([]);
    setSelectedAnomaly(null);
    try {
      localStorage.removeItem(ANOMALY_STORAGE_KEY);
    } catch {}
  };

  return (
    <AnomalyContext.Provider value={{ anomalyHistory, selectedAnomaly, setSelectedAnomaly, addAnomaly, updateAnomaly, clearHistory }}>
      {children}
    </AnomalyContext.Provider>
  );
};
