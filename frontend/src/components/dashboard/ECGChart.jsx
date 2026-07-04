import React from 'react';
import Plot from 'react-plotly.js';

const ECGChart = ({ xData, yData, predictions = [] }) => {
  // Tính toán các vùng bất thường (XAI) để vẽ đè lên biểu đồ
  const shapes = [];
  if (predictions && predictions.length > 0) {
    let startX = null;
    for (let i = 0; i < xData.length; i++) {
      const pred = predictions[i];
      const isAnomaly = pred && pred.includes('CẢNH BÁO');

      if (isAnomaly) {
        if (startX === null) {
          startX = xData[i];
        }
      } else {
        if (startX !== null) {
          shapes.push({
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: startX,
            x1: xData[i - 1],
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(239, 68, 68, 0.15)', // Màu đỏ nhạt làm nổi bật vùng lỗi
            line: { width: 0 }
          });
          startX = null;
        }
      }
    }
    // Trường hợp điểm bất thường kéo dài đến cuối danh sách hiện tại
    if (startX !== null) {
      shapes.push({
        type: 'rect',
        xref: 'x',
        yref: 'paper',
        x0: startX,
        x1: xData[xData.length - 1],
        y0: 0,
        y1: 1,
        fillcolor: 'rgba(239, 68, 68, 0.15)',
        line: { width: 0 }
      });
    }
  }

  return (
    <div className="card" style={{ width: '100%', height: '100%', minHeight: '350px', display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-main)', fontWeight: 'bold' }}>📡 Tín Hiệu ECG Thời Gian Thực</h3>
          {shapes.length > 0 && (
            <span style={{ padding: '2px 8px', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold' }}>
              🚨 Phát hiện nhịp bất thường (XAI)
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444', animation: 'pulse-danger 1s infinite' }}></span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Thời gian thực (10Hz)</span>
        </div>
      </div>
      
      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '0' }}>
        <Plot
          data={[{
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#ef4444', width: 2 }
          }]}
          layout={{
            autosize: true,
            plot_bgcolor: 'transparent', 
            paper_bgcolor: 'transparent',
            font: { color: '#64748b', family: 'Inter, sans-serif' },
            shapes: shapes, // Tích hợp các khối màu XAI đỏ nhạt
            xaxis: {
              showgrid: true,
              gridcolor: '#f1f5f9',
              zeroline: false,
              showticklabels: false,
              title: { text: 'Điểm dữ liệu', font: { size: 11 } }
            },
            yaxis: {
              showgrid: true,
              gridcolor: '#f1f5f9',
              zeroline: true,
              zerolinecolor: '#e2e8f0',
              range: [-1.2, 3.2]
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