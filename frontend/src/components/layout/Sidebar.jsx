import React from 'react';
import { useAuth } from '../../context/AuthContext';

const ADMIN_MENU_ITEMS = [
  { id: 'admin-overview', icon: '📊', label: 'Tổng Quan Hệ Thống' },
  { id: 'admin-users', icon: '👤', label: 'Quản Lý Tài Khoản' },
  { id: 'patient', icon: '🗂️', label: 'Hồ Sơ Bệnh Nhân' },
];

const CLINICAL_MENU_ITEMS = [
  { id: 'dashboard', icon: '📊', label: 'Theo Dõi Trực Tuyến' },
  { id: 'patient', icon: '🗂️', label: 'Hồ Sơ Bệnh Nhân' },
  { id: 'xai', icon: '🧠', label: 'Phân Tích XAI Chuyên Sâu' },
  { id: 'reports', icon: '📄', label: 'Xuất Báo Cáo (PDF/CSV)' },
  { id: 'settings', icon: '⚙️', label: 'Cài Đặt Hệ Thống' },
];

const Sidebar = ({ activeTab, setActiveTab }) => {
  const { isAdmin } = useAuth();
  // Admin quản trị hệ thống (tài khoản/bệnh nhân) - không xem cùng màn hình theo dõi real-time
  // với bác sĩ/y tá. "Cài Đặt Hệ Thống" (WS URL/ngưỡng cảnh báo) là tuỳ chọn của người trực
  // tiếp theo dõi màn hình, nên chuyển sang menu bác sĩ/y tá thay vì admin-only như trước.
  const menuItems = isAdmin ? ADMIN_MENU_ITEMS : CLINICAL_MENU_ITEMS;

  return (
    <nav style={{ 
      width: '260px', 
      minWidth: '260px', 
      backgroundColor: 'var(--sidebar-bg)', 
      display: 'flex', 
      flexDirection: 'column', 
      padding: '20px 0', 
      zIndex: 10
    }}>
      <div style={{ padding: '0 25px 20px', borderBottom: '1px solid rgba(255,255,255,0.1)', marginBottom: '15px' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: '#ffffff',
          color: '#000000',
          borderRadius: '12px',
          padding: '10px 12px',
          boxShadow: '0 8px 18px rgba(15, 23, 42, 0.08)',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <span style={{ fontSize: '22px' }}>🫀</span>
          <h2 style={{ margin: 0, color: '#000000', fontSize: '18px', fontWeight: '800', letterSpacing: '-0.04em' }}>
            NEURO-ECG
          </h2>
        </div>
        <p style={{ margin: '10px 0 0', fontSize: '12px', color: '#94a3b8' }}>Cloud Medical Platform</p>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', padding: '0 15px' }}>
        {menuItems.map(item => (
          <div 
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            style={{ 
              padding: '12px 15px', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px',
              cursor: 'pointer', 
              borderRadius: '6px',
              backgroundColor: activeTab === item.id ? 'var(--primary-bg)' : 'transparent',
              color: activeTab === item.id ? 'var(--text-sidebar-active)' : 'var(--text-sidebar)',
              fontWeight: activeTab === item.id ? '600' : '500',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== item.id) {
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            <span>{item.icon}</span> {item.label}
          </div>
        ))}
      </div>
    </nav>
  );
};

export default Sidebar;