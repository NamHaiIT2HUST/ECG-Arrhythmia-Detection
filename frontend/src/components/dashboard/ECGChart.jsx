import React from 'react';
import Plot from 'react-plotly.js';

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>Tín Hiệu ECG Thời Gian Thực</h3>
          {heatmap && (
            <span style={{ padding: '2px 8px', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: '4px', fontSize: '11px', fontWeight: '600', border: '1px solid #fca5a5' }} className="pulse-log-danger">
              Phát hiện bất thường (XAI)
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success)' }}></span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>1000 điểm (360 Hz)</span>
        </div>
      </div>
      
      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '0' }}>
        <Plot
          data={[{
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines',
            line: {
              color: '#2563eb', // Xanh dương classic
              width: 1.5,
            }
          }]}
          layout={{
            autosize: true,
            plot_bgcolor: 'transparent', 
            paper_bgcolor: 'transparent',
            font: { color: '#64748b', family: 'Inter, sans-serif' },
            shapes: shapes,
            xaxis: {
              showgrid: true,
              gridcolor: '#f1f5f9',
              zeroline: false,
              showticklabels: false,
              title: { text: 'Thời gian trôi (2.7s)', font: { size: 11, color: '#94a3b8' } }
            },
            yaxis: {
              showgrid: true,
              gridcolor: '#f1f5f9',
              zeroline: true,
              zerolinecolor: '#e2e8f0',
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