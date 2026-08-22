import React from 'react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Theo Dõi Trực Tuyến' },
    { id: 'patient', icon: '🗂️', label: 'Hồ Sơ Bệnh Nhân' },
    { id: 'xai', icon: '🧠', label: 'Phân Tích XAI Chuyên Sâu' },
  ];

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
        <h2 style={{ margin: 0, color: '#ffffff', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700' }}>
          <span style={{ fontSize: '22px' }}>🫀</span> NEURO-ECG
        </h2>
        <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#94a3b8' }}>Cloud Medical Platform</p>
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
              backgroundColor: activeTab === item.id ? 'var(--sidebar-active)' : 'transparent',
              color: activeTab === item.id ? 'var(--sidebar-active-text)' : 'var(--sidebar-text)',
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

      <div 
        onClick={() => setActiveTab('settings')}
        style={{ 
          margin: 'auto 15px 0',
          padding: '12px 15px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px',
          cursor: 'pointer', 
          borderRadius: '6px',
          backgroundColor: activeTab === 'settings' ? 'var(--sidebar-active)' : 'transparent',
          color: activeTab === 'settings' ? 'var(--sidebar-active-text)' : 'var(--sidebar-text)',
          fontWeight: activeTab === 'settings' ? '600' : '500',
          transition: 'all 0.15s ease'
        }}
        onMouseEnter={(e) => {
          if (activeTab !== 'settings') {
            e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)';
          }
        }}
        onMouseLeave={(e) => {
          if (activeTab !== 'settings') {
            e.currentTarget.style.backgroundColor = 'transparent';
          }
        }}
      >
        <span>⚙️</span> Cài Đặt Hệ Thống
      </div>
    </nav>
  );
};

export default Sidebar;