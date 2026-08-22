import React from 'react';

const StatCards = ({ latestPrediction, latency }) => {
  const isDanger = latestPrediction && latestPrediction.includes('CẢNH BÁO');
  
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px' }}>
      
      <div className="card" style={{ 
        padding: '20px 30px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : 'var(--card-bg)',
        borderLeft: isDanger ? '4px solid var(--danger)' : '4px solid var(--primary)',
      }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: isDanger ? 'var(--danger)' : 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🤖 Phân Tích AI
        </h3>
        <p style={{ 
          margin: 0, 
          fontSize: '28px', 
          fontWeight: '700', 
          color: isDanger ? 'var(--danger)' : 'var(--text-main)' 
        }}>
          {latestPrediction}
        </p>
      </div>

      <div className="card" style={{ 
        padding: '20px 30px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #94a3b8'
      }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          ⚡ Hiệu Suất Mô Hình (Latency)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
          <p style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>
            {latency}
          </p>
          <span style={{ fontSize: '16px', color: 'var(--text-muted)', fontWeight: '500' }}>mili-giây (ms) / nhịp</span>
        </div>
      </div>
      
    </div>
  );
};

export default StatCards;
