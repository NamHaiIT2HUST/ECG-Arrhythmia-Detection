import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const ECGChart = () => {
  const [xData, setXData] = useState(Array.from({ length: 100 }, (_, i) => i));
  const [yData, setYData] = useState(Array(100).fill(0));

  useEffect(() => {
    // Vẫn đang dùng dữ liệu giả để test UI, sau này thay bằng WebSocket
    const interval = setInterval(() => {
      setXData((prevX) => [...prevX.slice(1), prevX[prevX.length - 1] + 1]);
      setYData((prevY) => {
        const isHeartbeat = Math.random() > 0.9;
        const newValue = isHeartbeat ? Math.random() * 2 + 1 : Math.random() * 0.2 - 0.1;
        return [...prevY.slice(1), newValue];
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
      <Plot
        data={[
          {
            x: xData,
            y: yData,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#3f6ad8', width: 2.5 }, // Màu xanh biển hiện đại
            name: 'ECG Signal',
          },
        ]}
        layout={{
          plot_bgcolor: '#ffffff', // Nền biểu đồ trắng
          paper_bgcolor: '#ffffff', // Nền khung trắng
          font: { color: '#495057' }, // Chữ xám đậm
          xaxis: { showgrid: false, zeroline: false, showticklabels: false },
          yaxis: { showgrid: true, gridcolor: '#e9ecef', range: [-1, 3] }, // Lưới xám nhạt
          width: '100%',
          height: 350,
          margin: { l: 40, r: 20, t: 10, b: 20 },
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
};

export default ECGChart;