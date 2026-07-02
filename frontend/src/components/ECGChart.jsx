import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const ECGChart = () => {
  const [xData, setXData] = useState(Array.from({ length: 100 }, (_, i) => i));
  const [yData, setYData] = useState(Array(100).fill(0));

  useEffect(() => {
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
    // Bọc trong thẻ div có chiều cao 100%
    <div style={{ width: '100%', height: '100%', minHeight: '300px' }}>
      <Plot
        data={[{ x: xData, y: yData, type: 'scatter', mode: 'lines', line: { color: '#3f6ad8', width: 2.5 } }]}
        layout={{
          autosize: true, // Cho phép tự động co giãn
          plot_bgcolor: 'transparent', 
          paper_bgcolor: 'transparent',
          font: { color: '#495057' },
          xaxis: { showgrid: false, zeroline: false, showticklabels: false },
          yaxis: { showgrid: true, gridcolor: '#e9ecef', range: [-1, 3] },
          margin: { l: 40, r: 20, t: 10, b: 20 },
        }}
        useResizeHandler={true} // Kích hoạt resize
        style={{ width: '100%', height: '100%' }} // Ép full thẻ cha
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
};

export default ECGChart;