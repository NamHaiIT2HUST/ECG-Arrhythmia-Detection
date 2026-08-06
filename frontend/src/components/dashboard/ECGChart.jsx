import React from 'react';
import Plot from 'react-plotly.js';

const ECGChart = ({ xData, yData, heatmap = null }) => {
  // Tính toán vùng bất thường (XAI) để vẽ đè lên biểu đồ
  // Nếu có heatmap, vùng đó sẽ nằm ở 187 điểm cuối cùng của biểu đồ
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
      fillcolor: 'rgba(255, 0, 85, 0.15)', // Màu đỏ nhạt làm nổi bật vùng bệnh
      line: { 
        color: 'rgba(255, 0, 85, 0.5)', 
        width: 1 
      }
    });
  }

  // Neon style properties
  const neonLine = {
    color: '#00ff9d',
    width: 2,
    shape: 'spline' // Làm mượt đường
  };

  return (
    <div className="card" style={{ width: '100%', height: '100%', minHeight: '350px', display: 'flex', flexDirection: 'column', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ margin: 0, fontSize: '18px', color: 'var(--text-main)', fontWeight: 'bold' }}>📡 TÍN HIỆU ECG THỜI GIAN THỰC</h3>
          {heatmap && (
            <span style={{ padding: '4px 10px', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold', border: '1px solid var(--danger)' }} className="pulse-log-danger">
              🚨 PHÁT HIỆN BẤT THƯỜNG (XAI GRAD-CAM)
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', backgroundColor: 'var(--success)', boxShadow: '0 0 8px var(--success)' }}></span>
          <span style={{ fontSize: '14px', color: 'var(--success)', fontWeight: 'bold' }}>360 Hz</span>
        </div>
      </div>
      
      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '0' }}>
        <Plot
          data={[{
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines',
            line: neonLine,
            // Thêm hiệu ứng phát sáng mờ phía sau line
            fill: 'tozeroy',
            fillcolor: 'rgba(0, 255, 157, 0.05)'
          }]}
          layout={{
            autosize: true,
            plot_bgcolor: 'transparent', 
            paper_bgcolor: 'transparent',
            font: { color: '#64748b', family: 'Rajdhani, sans-serif' },
            shapes: shapes, // Tích hợp các khối màu XAI đỏ nhạt
            xaxis: {
              showgrid: true,
              gridcolor: 'rgba(0, 243, 255, 0.05)',
              zeroline: false,
              showticklabels: false,
              title: { text: 'Thời gian trôi (1000 điểm ~ 2.7s)', font: { size: 12, color: '#38bdf8' } }
            },
            yaxis: {
              showgrid: true,
              gridcolor: 'rgba(0, 243, 255, 0.05)',
              zeroline: true,
              zerolinecolor: 'rgba(0, 243, 255, 0.2)',
              range: [-2.0, 4.0] // Dải giá trị phù hợp với MIT-BIH
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