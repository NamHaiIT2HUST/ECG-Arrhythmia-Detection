import React from 'react';

const Header = ({ connectionStatus, latency }) => {
  const isConnected = connectionStatus && connectionStatus.includes('Đã kết nối');
  
  return (
    <header style={{ 
      height: '70px', 
      minHeight: '70px', 
      backgroundColor: '#ffffff', 
      borderBottom: '1px solid var(--border-color)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between', 
      padding: '0 25px', 
      zIndex: 5, 
      boxShadow: '0 2px 10px rgba(0,0,0,0.02)' 
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '20px', color: 'var(--text-main)', fontWeight: 'bold' }}>Hệ Thống Theo Dõi ECG Thời Gian Thực</h1>
        <span style={{ 
          padding: '4px 12px', 
          backgroundColor: isConnected ? '#dcfce7' : '#fef9c3', 
          color: isConnected ? '#15803d' : '#a16207', 
          borderRadius: '20px', 
          fontSize: '12px', 
          fontWeight: 'bold',
          transition: 'all 0.3s ease'
        }}>
          {isConnected ? '● Trực tuyến' : '▲ Mô phỏng'}
        </span>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {latency > 0 && (
          <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Độ trễ truyền tải: <strong style={{ color: 'var(--text-main)' }}>{latency}ms</strong>
          </span>
        )}
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--text-main)' }}>BS. Nguyễn Văn B</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Khoa Tim Mạch</div>
          </div>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '16px' }}>
            NB
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
