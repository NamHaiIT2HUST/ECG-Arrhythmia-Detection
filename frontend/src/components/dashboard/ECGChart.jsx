import React from 'react';
import Plot from 'react-plotly.js';

// Nền đen + sóng xanh lá là quy ước màn hình theo dõi bệnh nhân chuyên nghiệp (GE/Philips/
// Mindray...) - tương phản cao, dễ đọc kể cả phòng thiếu sáng, và bác sĩ đã quen mắt với màu
// này hơn hẳn so với nền xanh navy/vàng "app tiêu dùng" trước đây. Cố định luôn màu này bất
// kể theme sáng/tối của toàn app, vì đây là quy ước ngành riêng, không nên đổi theo theme UI.
const MONITOR_BG = '#04140a';
const MONITOR_TRACE = '#22ff88';
// Kênh tham chiếu thứ 2 (vd V1/V5) dùng màu cam/hổ phách - quy ước phổ biến trên monitor đa kênh
// để phân biệt rõ với kênh chẩn đoán chính (xanh lá) mà không cần đọc chú thích.
const MONITOR_TRACE_2 = '#f5b942';
const MONITOR_GRID = 'rgba(34, 255, 136, 0.12)';
const MONITOR_TEXT = 'rgba(226, 253, 238, 0.55)';

// "MLII" là tên nội bộ của PhysioNet/MIT-BIH ("Modified Lead II" - vị trí điện cực Holter cụ
// thể), bác sĩ đọc ECG chỉ biết "Lead II" - đổi tên hiển thị cho đúng ngôn ngữ lâm sàng, không
// đổi tên các lead ngực chuẩn khác (V1/V2/V4/V5...) vì chúng đã đúng quy ước rồi.
const formatLeadName = (name) => (name === 'MLII' ? 'II' : name);

const ECGChart = ({ xData, yData, yData2 = [], lead1Name: rawLead1Name = null, lead2Name: rawLead2Name = null, heatmap = null }) => {
  const lead1Name = formatLeadName(rawLead1Name);
  const lead2Name = formatLeadName(rawLead2Name);
  // Đa số bản ghi MIT-BIH có 2 kênh (vd MLII + V1/V5) - kênh 2 KHÔNG dùng để chẩn đoán AI (vẫn
  // là kênh 1 duy nhất), chỉ hiển thị thêm 1 dải sóng tham chiếu như máy Holter 2 kênh thật,
  // giúp bác sĩ đối chiếu hình dạng nhịp thay vì chỉ tin vào đúng 1 góc nhìn - xem
  // data_streamer.py và câu hỏi "sao chỉ hiện 1 dòng so với máy 12 lead" đã trao đổi.
  const hasLead2 = Array.isArray(yData2) && yData2.length > 0;

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
            {hasLead2
              ? `2 kênh (Lead ${lead1Name || 'II'} + ${lead2Name}) — sàng lọc rối loạn nhịp, không thay thế ECG 12 chuyển đạo chẩn đoán đầy đủ.`
              : `Đơn kênh (Lead ${lead1Name || 'II'}) — sàng lọc rối loạn nhịp, không thay thế ECG 12 chuyển đạo chẩn đoán đầy đủ.`}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0, marginTop: '2px' }}>
          <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--success)' }}></span>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{xData.length} điểm (360 Hz)</span>
        </div>
      </div>

      <div style={{ flex: 1, position: 'relative', width: '100%', height: '100%', minHeight: '0', borderRadius: '8px', overflow: 'hidden', backgroundColor: MONITOR_BG }}>
        <Plot
          data={hasLead2 ? [
            {
              x: xData,
              y: yData,
              type: 'scatter',
              mode: 'lines',
              xaxis: 'x',
              yaxis: 'y',
              line: { color: MONITOR_TRACE, width: 1.5 },
              name: lead1Name || 'Lead 1',
            },
            {
              x: xData,
              y: yData2,
              type: 'scatter',
              mode: 'lines',
              xaxis: 'x',
              yaxis: 'y2',
              line: { color: MONITOR_TRACE_2, width: 1.5 },
              name: lead2Name || 'Lead 2',
            },
          ] : [{
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
            showlegend: false,
            xaxis: {
              showgrid: true,
              gridcolor: MONITOR_GRID,
              zeroline: false,
              showticklabels: false,
              title: { text: `Thời gian trôi (${(xData.length / 360).toFixed(1)}s)`, font: { size: 11, color: MONITOR_TEXT } }
            },
            // Không có kênh 2: giữ nguyên 1 biểu đồ toàn khung như trước.
            // Có kênh 2: chia dọc thành 2 dải xếp chồng dùng CHUNG 1 trục x (giống bản in Holter
            // 2 kênh thật) - yaxis (trên) là kênh chẩn đoán chính, yaxis2 (dưới) là kênh tham chiếu.
            yaxis: hasLead2
              ? { domain: [0.56, 1], showgrid: true, gridcolor: MONITOR_GRID, zeroline: true, zerolinecolor: MONITOR_GRID, range: [-2.0, 4.0], title: { text: lead1Name || 'Lead 1', font: { size: 10, color: MONITOR_TEXT } } }
              : { showgrid: true, gridcolor: MONITOR_GRID, zeroline: true, zerolinecolor: MONITOR_GRID, range: [-2.0, 4.0] },
            ...(hasLead2 ? {
              yaxis2: { domain: [0, 0.44], showgrid: true, gridcolor: MONITOR_GRID, zeroline: true, zerolinecolor: MONITOR_GRID, range: [-2.0, 4.0], title: { text: lead2Name || 'Lead 2', font: { size: 10, color: MONITOR_TEXT } } },
            } : {}),
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