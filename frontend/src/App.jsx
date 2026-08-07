import React, { useState } from 'react';
import DashboardPage from './pages/DashboardPage';
import XAIPage from './pages/XAIPage';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Các state kết nối chung có thể được nhấc lên App.jsx nếu muốn, 
  // nhưng để gọn nhẹ, ta cứ giữ ở từng Page, hoặc pass connection từ App.
  // Ở đây dùng cấu trúc đơn giản là render theo Tab.

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-color)' }}>
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          {activeTab === 'dashboard' && <DashboardPage />}
          {activeTab === 'patient' && (
            <div style={{ padding: '25px' }}>
              <div className="card" style={{ padding: '40px', textAlign: 'center' }}>
                <h2 style={{ color: 'var(--text-main)' }}>Hồ Sơ Bệnh Nhân</h2>
                <p style={{ color: 'var(--text-muted)' }}>Tính năng quản lý hàng loạt hồ sơ bệnh nhân đang được phát triển.</p>
              </div>
            </div>
          )}
          {activeTab === 'xai' && <XAIPage />}
          {activeTab === 'settings' && (
            <div style={{ padding: '25px' }}>
              <div className="card" style={{ padding: '40px', textAlign: 'center' }}>
                <h2 style={{ color: 'var(--text-main)' }}>Cài Đặt Hệ Thống</h2>
                <p style={{ color: 'var(--text-muted)' }}>Cấu hình API Endpoint và phân quyền truy cập đang được phát triển.</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;