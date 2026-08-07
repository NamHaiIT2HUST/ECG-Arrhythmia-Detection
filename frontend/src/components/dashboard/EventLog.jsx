import React from 'react';

const EventLog = ({ logs }) => {
  return (
    <div className="card" style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', color: 'var(--text-main)', fontWeight: 'bold' }}>📋 Nhật Ký Cảnh Báo AI</h3>
      
      <div style={{ overflowY: 'auto', flex: 1, paddingRight: '5px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {logs.length === 0 ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '14px', fontStyle: 'italic' }}>
            Chưa có cảnh báo nào được ghi nhận.
          </div>
        ) : (
          logs.map(log => (
            <div 
              key={log.id} 
              className="card pulse-log-danger" 
              style={{ 
                padding: '12px', 
                backgroundColor: 'var(--danger-bg)', 
                borderLeft: '4px solid var(--danger)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                margin: '2px'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-muted)' }}>
                <span style={{ fontWeight: '500' }}>⏱️ {log.time}</span>
                <span style={{ color: 'var(--danger)', fontWeight: 'bold' }}>Biên độ: {log.value}</span>
              </div>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#b91c1c' }}>
                🚨 {log.prediction}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EventLog;