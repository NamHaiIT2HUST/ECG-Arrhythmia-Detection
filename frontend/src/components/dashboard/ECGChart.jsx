import React from 'react';
import Plot from 'react-plotly.js';

// Nền đen + sóng xanh lá là quy ước màn hình theo dõi bệnh nhân chuyên nghiệp (GE/Philips/
// Mindray...) - tương phản cao, dễ đọc kể cả phòng thiếu sáng, và bác sĩ đã quen mắt với màu
// này hơn hẳn so với nền xanh navy/vàng "app tiêu dùng" trước đây. Cố định luôn màu này bất
// kể theme sáng/tối của toàn app, vì đây là quy ước ngành riêng, không nên đổi theo theme UI.
const MONITOR_BG = '#04140a';
const MONITOR_TRACE = '#22ff88';
const MONITOR_GRID = 'rgba(34, 255, 136, 0.12)';
const MONITOR_TEXT = 'rgba(226, 253, 238, 0.55)';

const ECGChart = ({ xData, yData, heatmap = null }) => {
  const shapes = [];
  
  if (heatmap && xData.length >= 187) {
    const startX = xData[xData.length - 187];
    const endX = xData[xData.length - 1];
    
    shapes.push({
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: startX,
      x1: endX,
      y0: 0,
      y1: 1,
      fillcolor: 'rgba(239, 68, 68, 0.1)', // Đỏ siêu nhạt
      line: { 
        color: 'rgba(239, 68, 68, 0.4)', 
        width: 1 
      }
    });
  }

  return (
    <div className="card" style={{ width: '100%', height: '100%', minHeight: '350px', display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>Tín Hiệu ECG Thời Gian Thực</h3>
            {heatmap && (
              <span style={{ padding: '2px 8px', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '4px', fontSize: '11px', fontWeight: '600', border: '1px solid #fca5a5' }} className="pulse-log-danger">
                Phát hiện bất thường (XAI)
              </span>
            )}
          </div>
          <p style={{ margin: '3px 0 0', fontSize: '11.5px', color: 'var(--text-muted)' }}>
            Đơn kênh (Lead II/MLII) — sàng lọc rối loạn nhịp, không thay thế ECG 12 chuyển đạo chẩn đoán đầy đủ.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginTop: '2px' }}>
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success)' }}></span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{xData.length} điểm (360 Hz)</span>
        </div>
      </div>

      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '0', borderRadius: '8px', overflow: 'hidden', backgroundColor: MONITOR_BG }}>
        <Plot
          data={[{
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines',
            line: {
              color: MONITOR_TRACE,
              width: 1.5,
            }
          }]}
          layout={{
            autosize: true,
            plot_bgcolor: 'transparent',
            paper_bgcolor: 'transparent',
            font: { color: MONITOR_TEXT, family: 'Inter, sans-serif' },
            shapes: shapes,
            xaxis: {
              showgrid: true,
              gridcolor: MONITOR_GRID,
              zeroline: false,
              showticklabels: false,
              title: { text: `Thời gian trôi (${(xData.length / 360).toFixed(1)}s)`, font: { size: 11, color: MONITOR_TEXT } }
            },
            yaxis: {
              showgrid: true,
              gridcolor: MONITOR_GRID,
              zeroline: true,
              zerolinecolor: MONITOR_GRID,
              range: [-2.0, 4.0]
            },
            margin: { l: 30, r: 10, t: 10, b: 30 },
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
          config={{ displayModeBar: false, responsive: true }}
        />
      </div>
    </div>
  );
};

export default ECGChart;