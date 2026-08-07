import React from 'react';

const Header = ({ connectionStatus, latency }) => {
  // Xác định text và style cho badge trạng thái
  let badgeText = '⏳ Đang kết nối...';
  let badgeBg = '#fef9c3'; // yellow-50
  let badgeColor = '#854d0e'; // yellow-800
  
  if (connectionStatus === 'Đã kết nối') {
    badgeText = '● Trực tuyến';
    badgeBg = '#dcfce7'; // green-100
    badgeColor = '#15803d'; // green-700
  } else if (connectionStatus === 'Đang kết nối lại...') {
    badgeText = '⚠️ Đang kết nối lại...';
    badgeBg = '#fef9c3'; // yellow-100
    badgeColor = '#a16207'; // yellow-700
  } else if (connectionStatus.includes('Mô phỏng')) {
    badgeText = '▲ Mô phỏng';
    badgeBg = '#dbeafe'; // blue-100
    badgeColor = '#1e40af'; // blue-800
  }

  return (
    <header style={{ 
      height: '70px', 
      minHeight: '70px', 
      backgroundColor: 'rgba(8, 12, 20, 0.6)', 
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border-color)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between', 
      padding: '0 25px', 
      zIndex: 5, 
      boxShadow: '0 2px 10px rgba(0,0,0,0.02)' 
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '22px', color: 'var(--primary)', textShadow: '0 0 10px rgba(0, 243, 255, 0.3)' }}>HỆ THỐNG THEO DÕI ECG THỜI GIAN THỰC</h1>
        <span style={{ 
          padding: '4px 12px', 
          backgroundColor: badgeBg, 
          color: badgeColor, 
          borderRadius: '20px', 
          fontSize: '12px', 
          fontWeight: 'bold',
          transition: 'all 0.3s ease'
        }}>
          {badgeText}
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
