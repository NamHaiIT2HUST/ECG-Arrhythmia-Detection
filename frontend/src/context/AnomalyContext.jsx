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

  // CP5.4: dùng sau khi bác sĩ xác nhận/sửa nhãn AI (XAIPage) - cập nhật đồng thời cả item
  // trong danh sách lịch sử VÀ bản đang xem chi tiết (2 object khác nhau sau addAnomaly, nếu
  // chỉ sửa 1 bên sẽ lệch trạng thái giữa list và khung chi tiết).
  const updateAnomaly = (id, patch) => {
    setAnomalyHistory(prev => prev.map(item => (item.id === id ? { ...item, ...patch } : item)));
    setSelectedAnomaly(prev => (prev && prev.id === id ? { ...prev, ...patch } : prev));
  };

  // Gọi khi đổi bệnh nhân/bản ghi đang theo dõi (MonitoringContext) - lịch sử cảnh báo là của
  // 1 phiên theo dõi 1 bệnh nhân, không xoá sẽ lẫn cảnh báo của nhiều bệnh nhân khác nhau
  // trong cùng phiên trình duyệt (ảnh hưởng cả trang XAI lẫn báo cáo xuất theo bệnh nhân).
  const clearHistory = () => {
    setAnomalyHistory([]);
    setSelectedAnomaly(null);
  };

  return (
    <AnomalyContext.Provider value={{ anomalyHistory, selectedAnomaly, setSelectedAnomaly, addAnomaly, updateAnomaly, clearHistory }}>
      {children}
    </AnomalyContext.Provider>
  );
};
