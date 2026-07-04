import React from 'react';

const LoadingSpinner = () => {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100%', 
      width: '100%',
      minHeight: '400px',
      gap: '20px',
      color: 'var(--text-muted)'
    }}>
      <div className="spinner" style={{
        width: '50px',
        height: '50px',
        border: '5px solid var(--border-color)',
        borderTop: '5px solid var(--primary)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }}></div>
      <div style={{ fontSize: '16px', fontWeight: '500', letterSpacing: '0.5px' }}>
        Đang thiết lập kết nối với máy chủ ECG...
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
