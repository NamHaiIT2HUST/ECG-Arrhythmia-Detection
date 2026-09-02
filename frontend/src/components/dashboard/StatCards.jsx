import React from 'react';

const StatCards = ({ latestPrediction, latency, bpm, hrv_sdnn, confidence }) => {
  const isDanger = latestPrediction && latestPrediction.includes('CẢNH BÁO');
  
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px' }}>
      
      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : 'var(--card-bg)',
        borderLeft: isDanger ? '4px solid var(--danger)' : '4px solid var(--primary)',
        gridColumn: 'span 2'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: isDanger ? 'var(--danger)' : 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🤖 Phân Tích AI
        </h3>
        <p style={{ 
          margin: 0, 
          fontSize: '22px', 
          fontWeight: '700', 
          color: isDanger ? 'var(--danger)' : 'var(--text-main)' 
        }}>
          {latestPrediction}
        </p>
      </div>

      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #f59e0b'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          💓 Nhịp tim (BPM)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {bpm ?? '--'}
          </p>
        </div>
      </div>

      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #10b981'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          📈 HRV (SDNN)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {hrv_sdnn ? hrv_sdnn.toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>ms</span>
        </div>
      </div>

      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #8b5cf6'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🎯 Độ tin cậy AI
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {confidence ? (confidence * 100).toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>%</span>
        </div>
      </div>
      
    </div>
  );
};

export default StatCards;
