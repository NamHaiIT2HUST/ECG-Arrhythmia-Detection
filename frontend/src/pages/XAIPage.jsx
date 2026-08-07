import React from 'react';

const XAIPage = () => {
  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      <div className="card" style={{ padding: '30px' }}>
        <h2 style={{ margin: '0 0 10px 0', color: 'var(--text-main)', fontSize: '20px' }}>🧠 Phân Tích XAI Chuyên Sâu (1D Grad-CAM)</h2>
        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.6 }}>
          Khu vực này dùng để nghiên cứu và mổ xẻ quyết định của AI đối với từng nhịp tim bất thường.
          Hệ thống sẽ bóc tách các layer của ResNet1D và trích xuất Grad-CAM Heatmap chi tiết hơn (so với biểu đồ live ở Dashboard).
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', flex: 1 }}>
        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '15px' }}>Lịch Sử Cảnh Báo Gần Đây</h3>
          <div style={{ flex: 1, border: '1px dashed var(--border-color)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8fafc' }}>
            <p style={{ color: 'var(--text-muted)' }}>Đang chờ đồng bộ dữ liệu lịch sử...</p>
          </div>
        </div>

        <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '15px' }}>Chi Tiết Phân Phối Trọng Số (Weights)</h3>
          <div style={{ flex: 1, border: '1px dashed var(--border-color)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8fafc' }}>
            <p style={{ color: 'var(--text-muted)' }}>Vui lòng chọn một nhịp tim để phân tích</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default XAIPage;
