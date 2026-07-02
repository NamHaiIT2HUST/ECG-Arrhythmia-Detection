import React, { useState, useEffect } from 'react';
import ECGChart from './components/ECGChart';

function App() {
  const [systemStatus, setSystemStatus] = useState("BÌNH THƯỜNG");
  
  // Nhúng CSS trực tiếp để tạo hiệu ứng xịn xò
  const cssStyles = `
    .hover-card {
      transition: all 0.3s ease;
    }
    .hover-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
    }
    @keyframes pulse-green {
      0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
      70% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
      100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    .pulse-dot {
      animation: pulse-green 2s infinite;
    }
  `;

  const styles = {
    appContainer: { display: 'flex', height: '100vh', width: '100vw', fontFamily: 'Segoe UI, Arial, sans-serif', backgroundColor: '#f4f7f6', color: '#333', overflow: 'hidden' },
    sidebar: { width: '260px', minWidth: '260px', backgroundColor: '#1e293b', color: '#fff', display: 'flex', flexDirection: 'column', padding: '20px 0', zIndex: 10, boxShadow: '4px 0 10px rgba(0,0,0,0.05)' },
    logoArea: { padding: '0 20px 20px', borderBottom: '1px solid #334155', marginBottom: '20px' },
    menuItem: { padding: '15px 25px', display: 'flex', alignItems: 'center', cursor: 'pointer', transition: '0.2s', borderLeft: '4px solid transparent' },
    menuItemActive: { backgroundColor: '#334155', borderLeft: '4px solid #38bdf8', fontWeight: 'bold' },
    rightArea: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' },
    header: { height: '70px', minHeight: '70px', backgroundColor: '#fff', borderBottom: '1px solid #e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px', boxShadow: '0 2px 5px rgba(0,0,0,0.02)' },
    mainContent: { flex: 1, padding: '25px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '25px' },
    card: { backgroundColor: '#fff', padding: '20px', borderRadius: '10px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column' },
  };

  return (
    <div style={styles.appContainer}>
      <style>{cssStyles}</style> {/* Tiêm CSS vào đây */}
      
      {/* SIDEBAR */}
      <nav style={styles.sidebar}>
        <div style={styles.logoArea}>
          <h2 style={{ margin: 0, color: '#38bdf8', fontSize: '22px', textShadow: '0 0 10px rgba(56,189,248,0.3)' }}>🫀 CardioAI</h2>
          <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#94a3b8' }}>Real-time Edge Monitor</p>
        </div>
        <div style={{ ...styles.menuItem, ...styles.menuItemActive }}>📊 Theo Dõi Trực Tuyến</div>
        <div className="hover-card" style={styles.menuItem}>🗂️ Hồ Sơ Bệnh Nhân</div>
        <div className="hover-card" style={styles.menuItem}>⚙️ Cấu Hình Cảm Biến</div>
      </nav>

      <div style={styles.rightArea}>
        {/* HEADER */}
        <header style={styles.header}>
          <div>
            <h2 style={{ margin: 0, fontSize: '20px' }}>Dashboard Trực Tuyến</h2>
            <span style={{ fontSize: '13px', color: '#64748b' }}>Phòng Điều Trị Tích Cực (ICU) - Giường 04</span>
          </div>
          <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
            <span style={{ padding: '6px 14px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '20px', fontSize: '13px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid #bbf7d0' }}>
              {/* Thêm class pulse-dot vào đây */}
              <span className="pulse-dot" style={{width: '10px', height: '10px', backgroundColor: '#22c55e', borderRadius: '50%', display: 'inline-block'}}></span> Online
            </span>
            <div style={{ width: '40px', height: '40px', backgroundColor: '#f1f5f9', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: '#3b82f6', border: '2px solid #e2e8f0', cursor: 'pointer' }} className="hover-card">
              AD
            </div>
          </div>
        </header>

        {/* NỘI DUNG CHÍNH */}
        <main style={styles.mainContent}>
          {/* HÀNG 1 */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
            <div className="hover-card" style={{ ...styles.card, borderTop: '4px solid #ef4444' }}>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 'bold' }}>TRẠNG THÁI AI</span>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: systemStatus === 'BÌNH THƯỜNG' ? '#22c55e' : '#ef4444', marginTop: '5px' }}>{systemStatus}</div>
            </div>
            <div className="hover-card" style={{ ...styles.card, borderTop: '4px solid #3b82f6' }}>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 'bold' }}>NHỊP TIM</span>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0f172a', marginTop: '5px' }}>78 <span style={{ fontSize: '14px', color: '#64748b' }}>BPM</span></div>
            </div>
            <div className="hover-card" style={{ ...styles.card, borderTop: '4px solid #f59e0b' }}>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 'bold' }}>ĐỘ TRỄ (LATENCY)</span>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0f172a', marginTop: '5px' }}>14 <span style={{ fontSize: '14px', color: '#64748b' }}>ms</span></div>
            </div>
            <div className="hover-card" style={{ ...styles.card, borderTop: '4px solid #8b5cf6' }}>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 'bold' }}>MODEL ENGINE</span>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0f172a', marginTop: '5px' }}>CNN-GRU</div>
            </div>
          </div>

          {/* HÀNG 2 */}
          <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: '0' }}>
            {/* CỘT TRÁI */}
            <div className="hover-card" style={{ ...styles.card, flex: 7, padding: '0', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '15px 20px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc' }}>
                <h3 style={{ margin: 0, fontSize: '16px' }}>Biểu Đồ Điện Tâm Đồ (Kênh I)</h3>
                <span style={{ fontSize: '12px', backgroundColor: '#e2e8f0', padding: '4px 10px', borderRadius: '4px', color: '#475569', fontWeight: 'bold' }}>Auto-scale: BẬT</span>
              </div>
              {/* Vùng chứa Chart dãn kín */}
              <div style={{ flex: 1, padding: '10px 20px 20px 20px', display: 'flex' }}>
                <ECGChart />
              </div>
            </div>

            {/* CỘT PHẢI */}
            <div style={{ flex: 3, display: 'flex', flexDirection: 'column', gap: '20px', minHeight: '0' }}>
              <div className="hover-card" style={{ ...styles.card, flex: 'none' }}>
                <h3 style={{ margin: '0 0 15px 0', fontSize: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>Thông Tin Bệnh Nhân</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ color: '#64748b', fontSize: '14px' }}>Họ tên:</span><span style={{ fontWeight: 'bold' }}>Nguyễn Văn A</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span style={{ color: '#64748b', fontSize: '14px' }}>Mã BA:</span><span style={{ fontWeight: 'bold' }}>BN-2026-89</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#64748b', fontSize: '14px' }}>Tuổi / Giới tính:</span><span style={{ fontWeight: 'bold' }}>45 / Nam</span>
                </div>
              </div>

              <div className="hover-card" style={{ ...styles.card, flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <h3 style={{ margin: '0 0 10px 0', fontSize: '16px' }}>Nhật Ký AI (Event Log)</h3>
                <div style={{ overflowY: 'auto', flex: 1, paddingRight: '5px' }}>
                  <div style={{ padding: '10px', backgroundColor: '#fef2f2', borderRadius: '6px', marginBottom: '8px', borderLeft: '3px solid #ef4444', transition: '0.2s' }} className="hover-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>
                      <span>14:30:45</span><span style={{ color: '#ef4444', fontWeight: 'bold' }}>98%</span>
                    </div>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#7f1d1d' }}>Phát hiện PVC</div>
                  </div>
                  <div style={{ padding: '10px', backgroundColor: '#f1f5f9', borderRadius: '6px', marginBottom: '8px', borderLeft: '3px solid #94a3b8' }} className="hover-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>
                      <span>14:28:12</span><span style={{ color: '#0f172a', fontWeight: 'bold' }}>--</span>
                    </div>
                    <div style={{ fontSize: '14px', color: '#334155' }}>Hệ thống đã kết nối</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;