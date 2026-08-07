import React from 'react';
import { useAnomaly } from '../context/AnomalyContext';
import Plot from 'react-plotly.js';

const XAIPage = () => {
  const { anomalyHistory, selectedAnomaly, setSelectedAnomaly } = useAnomaly();

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      
      <div className="card" style={{ padding: '20px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: '0 0 5px 0', color: 'var(--text-main)', fontSize: '20px' }}>🧠 Trạm Phân Tích XAI (1D Grad-CAM)</h2>
          <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '14px' }}>
            Nghiên cứu vùng trọng số (Heatmap) của mô hình ResNet1D trên các nhịp tim lỗi (PVC).
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Tổng số nhịp lỗi đã lưu:</span>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--danger)' }}>{anomalyHistory.length}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 3fr', gap: '20px', flex: 1, minHeight: 0 }}>
        
        {/* Lịch sử nhịp lỗi */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '15px 20px', borderBottom: '1px solid var(--border-color)', backgroundColor: '#f8fafc' }}>
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '600', color: 'var(--text-main)' }}>Lịch Sử Cảnh Báo</h3>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
            {anomalyHistory.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', marginTop: '20px' }}>Chưa có cảnh báo nào.</p>
            ) : (
              anomalyHistory.map((item) => (
                <div 
                  key={item.id} 
                  onClick={() => setSelectedAnomaly(item)}
                  style={{ 
                    padding: '12px 15px', 
                    border: '1px solid',
                    borderColor: selectedAnomaly?.id === item.id ? 'var(--primary)' : 'var(--border-color)',
                    borderRadius: '6px',
                    marginBottom: '8px',
                    cursor: 'pointer',
                    backgroundColor: selectedAnomaly?.id === item.id ? 'var(--primary-bg)' : '#ffffff',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--danger)', marginBottom: '4px' }}>🚨 {item.prediction}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{item.time}</span>
                    <span>{item.latency} ms</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Khung phân tích chi tiết */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', padding: '20px' }}>
          <h3 style={{ margin: '0 0 15px 0', fontSize: '15px', color: 'var(--text-main)' }}>Giải phẫu trọng số mô hình (Weights Anatomy)</h3>
          
          <div style={{ flex: 1, border: '1px dashed var(--border-color)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#fafaf9', position: 'relative' }}>
            {!selectedAnomaly || !selectedAnomaly.signal ? (
              <p style={{ color: 'var(--text-muted)' }}>Vui lòng chọn một nhịp tim lỗi ở danh sách bên trái.</p>
            ) : (
              <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}>
                <Plot
                  data={[
                    // Vẽ Heatmap dạng Bar (đổ bóng màu từ dưới lên)
                    {
                      x: Array.from({length: 187}, (_, i) => i),
                      y: selectedAnomaly.heatmap,
                      type: 'bar',
                      marker: {
                        color: selectedAnomaly.heatmap,
                        colorscale: 'Reds',
                        showscale: true,
                        colorbar: { title: 'Độ chú ý', titleside: 'right', tickfont: { size: 10 } }
                      },
                      opacity: 0.7,
                      name: 'Grad-CAM'
                    },
                    // Vẽ Sóng ECG đè lên trên
                    {
                      x: Array.from({length: 187}, (_, i) => i),
                      y: selectedAnomaly.signal,
                      type: 'scatter',
                      mode: 'lines',
                      line: { color: '#0f172a', width: 2 },
                      name: 'Tín hiệu ECG'
                    }
                  ]}
                  layout={{
                    autosize: true,
                    plot_bgcolor: 'transparent', 
                    paper_bgcolor: 'transparent',
                    font: { family: 'Inter, sans-serif' },
                    margin: { l: 40, r: 20, t: 30, b: 40 },
                    title: { text: `Phân tích mẫu thử lúc ${selectedAnomaly.time}`, font: { size: 13, color: '#64748b' } },
                    xaxis: { title: 'Chỉ số mẫu (0-186)', showgrid: false },
                    yaxis: { title: 'Biên độ chuẩn hóa', showgrid: true, gridcolor: '#e2e8f0' },
                    showlegend: false
                  }}
                  useResizeHandler={true}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false, responsive: true }}
                />
              </div>
            )}
          </div>
          
          {selectedAnomaly && (
            <div style={{ marginTop: '15px', padding: '15px', backgroundColor: 'var(--danger-bg)', borderRadius: '6px', border: '1px solid #fecaca' }}>
              <p style={{ margin: 0, fontSize: '13px', color: '#991b1b', lineHeight: 1.5 }}>
                <strong>Kết luận XAI:</strong> Mô hình ResNet1D đã tập trung sự chú ý cao nhất vào các vùng màu đỏ sậm (giá trị heatmap ≈ 1.0). 
                Điều này khớp với đặc trưng lâm sàng của phức bộ QRS dị dạng dãn rộng trong nhịp <strong>{selectedAnomaly.prediction}</strong>.
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default XAIPage;
