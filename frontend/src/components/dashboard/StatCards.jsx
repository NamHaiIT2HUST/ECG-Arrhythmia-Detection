import React from 'react';

const StatCards = ({ latestPrediction, connectionStatus, latency }) => {
  const isDanger = latestPrediction && latestPrediction.includes('CẢNH BÁO');
  
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
      {/* Card 1: Nhịp Tim */}
      <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)', fontWeight: 'bold' }}>💓 Nhịp Tim (BPM)</h3>
        <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: 'var(--text-main)' }}>75</p>
        <span style={{ fontSize: '12px', color: 'var(--success)', fontWeight: '500' }}>▲ Bình thường</span>
      </div>

      {/* Card 2: Trạng Thái AI */}
      <div className="card" style={{ 
        padding: '20px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : 'var(--card-bg)',
        borderLeft: isDanger ? '4px solid var(--danger)' : '1px solid var(--border-color)',
        transition: 'all 0.3s ease'
      }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: isDanger ? 'var(--danger)' : 'var(--text-muted)', fontWeight: 'bold' }}>🤖 Chẩn Đoán AI</h3>
        <p style={{ 
          margin: 0, 
          fontSize: '22px', 
          fontWeight: 'bold', 
          color: isDanger ? 'var(--danger)' : 'var(--success)' 
        }}>
          {latestPrediction}
        </p>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Độ trễ AI: <strong style={{ color: 'var(--text-main)' }}>{latency} ms</strong>
        </span>
      </div>

      {/* Card 3: Nhiệt Độ */}
      <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)', fontWeight: 'bold' }}>🌡️ Nhiệt Độ</h3>
        <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: 'var(--text-main)' }}>36.5 °C</p>
        <span style={{ fontSize: '12px', color: 'var(--success)', fontWeight: '500' }}>▲ Bình thường</span>
      </div>

      {/* Card 4: Kết Nối */}
      <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)', fontWeight: 'bold' }}>🔗 Hệ Thống</h3>
        <p style={{ 
          margin: 0, 
          fontSize: '20px', 
          fontWeight: 'bold', 
          color: connectionStatus.includes('Đã kết nối') ? 'var(--success)' : '#eab308' 
        }}>
          {connectionStatus}
        </p>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Dịch vụ: <strong style={{ color: 'var(--text-main)' }}>ws/ecg</strong>
        </span>
      </div>
    </div>
  );
};

export default StatCards;
