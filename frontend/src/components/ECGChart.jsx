import Plot from 'react-plotly.js';

function ECGChart({ data }) {
  return (
    <Plot
      data={[{ x: data.x, y: data.y, type: 'scatter', mode: 'lines', marker: {color: 'red'} }]}
      layout={{ width: 600, height: 400, title: 'Real-time ECG' }}
    />
  );
}
export default ECGChart;