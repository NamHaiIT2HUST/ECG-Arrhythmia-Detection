import React from 'react';
import ECGChart from './components/ECGChart';

function App() {
  // Định nghĩa style tái sử dụng cho các thẻ (Cards)
  const cardStyle = {
    backgroundColor: '#ffffff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)', // Đổ bóng nhẹ
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    border: '1px solid #e9ecef',
  };

  return (
    <div style={{ fontFamily: 'Segoe UI, Arial, sans-serif', backgroundColor: '#f1f4f6', color: '#495057', minHeight: '100vh', padding: '30px' }}>
      
      {/* Header */}
      <header style={{ marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, color: '#3f6ad8', fontSize: '24px' }}>Hệ Thống Theo Dõi Điện Tâm Đồ</h1>
          <p style={{ margin: '5px 0 0 0', color: '#888', fontSize: '14px' }}>Real-time Dashboard Monitoring</p>
        </div>
        <div>
          {/* Nút giả lập Action như trong ảnh */}
          <button style={{ backgroundColor: '#3f6ad8', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' }}>
            Xuất Báo Cáo
          </button>
        </div>
      </header>

      {/* Khu vực Top Metrics (Các hộp nhỏ ở trên) */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        
        {/* Box 1: Viền Đỏ */}
        <div style={{ ...cardStyle, borderTop: '4px solid #d92550' }}>
          <span style={{ fontSize: '12px', color: '#888', textTransform: 'uppercase', fontWeight: 'bold' }}>Trạng Thái AI</span>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#d92550', marginTop: '10px' }}>CẢNH BÁO PVC</div>
        </div>

        {/* Box 2: Viền Xanh biển */}
        <div style={{ ...cardStyle, borderTop: '4px solid #3f6ad8' }}>
          <span style={{ fontSize: '12px', color: '#888', textTransform: 'uppercase', fontWeight: 'bold' }}>Nhịp Tim (BPM)</span>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#333', marginTop: '10px' }}>
            85 <span style={{ fontSize: '14px', color: '#888' }}>bpm</span>
          </div>
        </div>

        {/* Box 3: Viền Vàng */}
        <div style={{ ...cardStyle, borderTop: '4px solid #f7b924' }}>
          <span style={{ fontSize: '12px', color: '#888', textTransform: 'uppercase', fontWeight: 'bold' }}>Độ Trễ Phản Hồi</span>
          <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#333', marginTop: '10px' }}>
            12 <span style={{ fontSize: '14px', color: '#888' }}>ms</span>
          </div>
        </div>

        {/* Box 4: Viền Xanh lá */}
        <div style={{ ...cardStyle, borderTop: '4px solid #3ac47d' }}>
          <span style={{ fontSize: '12px', color: '#888', textTransform: 'uppercase', fontWeight: 'bold' }}>Kết Nối Dữ Liệu</span>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#3ac47d', marginTop: '10px' }}>TRỰC TUYẾN</div>
        </div>

      </section>

      {/* Khu vực Biểu đồ Chính */}
      <section style={{ display: 'flex', gap: '20px' }}>
        
        {/* Biểu đồ ECG */}
        <div style={{ ...cardStyle, flex: 3, borderTop: 'none' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ margin: 0, color: '#333' }}>Tín Hiệu ECG Thời Gian Thực</h3>
            <span style={{ backgroundColor: '#f7b924', color: 'white', padding: '2px 10px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>LIVE</span>
          </div>
          <ECGChart />
        </div>

        {/* Cột thông tin phụ bên phải */}
        <div style={{ ...cardStyle, flex: 1, borderTop: 'none', justifyContent: 'flex-start' }}>
          <h3 style={{ margin: '0 0 20px 0', color: '#333' }}>Cấu Hình Hệ Thống</h3>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ fontSize: '12px', color: '#888' }}>Model Đang Chạy</div>
            <div style={{ fontWeight: 'bold', color: '#333' }}>CNN 1D (Baseline)</div>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ fontSize: '12px', color: '#888' }}>Nguồn Dữ Liệu</div>
            <div style={{ fontWeight: 'bold', color: '#333' }}>MIT-BIH Database</div>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ fontSize: '12px', color: '#888' }}>Bộ lọc Nhiễu</div>
            <div style={{ fontWeight: 'bold', color: '#333' }}>Butterworth Bandpass</div>
          </div>
        </div>

      </section>

    </div>
  );
}

export default App;