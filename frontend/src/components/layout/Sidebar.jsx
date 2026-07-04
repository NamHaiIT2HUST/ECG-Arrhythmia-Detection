import React from 'react';

const Sidebar = () => {
  return (
    <nav style={{ 
      width: '260px', 
      minWidth: '260px', 
      backgroundColor: 'var(--sidebar-bg)', 
      color: '#ffffff', 
      display: 'flex', 
      flexDirection: 'column', 
      padding: '20px 0', 
      zIndex: 10, 
      boxShadow: '4px 0 10px rgba(0,0,0,0.05)' 
    }}>
      <div style={{ padding: '0 25px 20px', borderBottom: '1px solid #334155', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, color: 'var(--accent)', fontSize: '22px', textShadow: '0 0 10px rgba(56,189,248,0.3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🫀</span> ECG-Arrhythmia-Detection
        </h2>
        <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#94a3b8' }}>Real-time Edge Monitor</p>
      </div>
      
      <div style={{ 
        padding: '15px 25px', 
        display: 'flex', 
        alignItems: 'center', 
        gap: '12px',
        cursor: 'pointer', 
        transition: 'all 0.2s ease', 
        backgroundColor: 'var(--sidebar-active)', 
        borderLeft: '4px solid var(--accent)', 
        fontWeight: 'bold',
        fontSize: '14px'
      }}>
        <span>📊</span> Theo Dõi Trực Tuyến
      </div>
      
      <div 
        style={{ 
          padding: '15px 25px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px',
          cursor: 'pointer', 
          transition: 'all 0.2s ease', 
          borderLeft: '4px solid transparent', 
          fontSize: '14px',
          color: '#cbd5e1'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--sidebar-active)';
          e.currentTarget.style.color = '#ffffff';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = '#cbd5e1';
        }}
      >
        <span>🗂️</span> Hồ Sơ Bệnh Nhân
      </div>

      <div 
        style={{ 
          padding: '15px 25px', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px',
          cursor: 'pointer', 
          transition: 'all 0.2s ease', 
          borderLeft: '4px solid transparent', 
          fontSize: '14px',
          color: '#cbd5e1',
          marginTop: 'auto'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--sidebar-active)';
          e.currentTarget.style.color = '#ffffff';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = '#cbd5e1';
        }}
      >
        <span>⚙️</span> Cài Đặt Hệ Thống
      </div>
    </nav>
  );
};

export default Sidebar;