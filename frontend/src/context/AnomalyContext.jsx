import React, { createContext, useState, useContext } from 'react';

const AnomalyContext = createContext();

export const useAnomaly = () => useContext(AnomalyContext);

export const AnomalyProvider = ({ children }) => {
  // Lưu trữ lịch sử các nhịp tim lỗi
  const [anomalyHistory, setAnomalyHistory] = useState([]);
  
  // Lưu nhịp tim đang được xem chi tiết
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);

  const addAnomaly = (anomalyData) => {
    setAnomalyHistory(prev => {
      // Tránh duplicate (spam) nếu cùng 1 khoảng thời gian ngắn
      const last = prev[0];
      if (last && (Date.now() - last.timestamp < 2000)) {
        return prev;
      }
      
      const newAnomaly = {
        ...anomalyData,
        id: Date.now(),
        timestamp: Date.now(),
        time: new Date().toLocaleTimeString(),
      };
      
      const newHistory = [newAnomaly, ...prev].slice(0, 20); // Giữ 20 lỗi gần nhất
      
      // Auto select nếu chưa có gì
      if (!selectedAnomaly) {
        setSelectedAnomaly(newAnomaly);
      }
      
      return newHistory;
    });
  };

  return (
    <AnomalyContext.Provider value={{ anomalyHistory, selectedAnomaly, setSelectedAnomaly, addAnomaly }}>
      {children}
    </AnomalyContext.Provider>
  );
};
