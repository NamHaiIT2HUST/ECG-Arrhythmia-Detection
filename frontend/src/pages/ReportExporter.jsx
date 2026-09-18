import React, { useState, useMemo } from 'react';
import { usePatient } from '../context/PatientContext';
import { useAnomaly } from '../context/AnomalyContext';
import { generateCSV, generatePDF } from '../utils/reportGenerator';

const ReportExporter = () => {
  const { patients, selectedPatient } = usePatient();
  const { anomalyHistory } = useAnomaly();
  const [chosenId, setChosenId] = useState(selectedPatient?.id ?? '');
  const [isExporting, setIsExporting] = useState(false);

  const chosenPatient = useMemo(
    () => patients.find(p => String(p.id) === String(chosenId)) || null,
    [patients, chosenId]
  );

  // Lịch sử cảnh báo (AnomalyContext) chỉ thuộc về bệnh nhân ĐANG/vừa được theo dõi trong
  // phiên trình duyệt này (MonitoringContext xoá lịch sử mỗi khi đổi bệnh nhân) - nên báo cáo
  // chỉ có dữ liệu ý nghĩa khi bệnh nhân được chọn ở đây trùng với bệnh nhân đang theo dõi.
  const hasSessionData = !!chosenPatient && chosenPatient.id === selectedPatient?.id;
  const stats = useMemo(() => {
    if (!hasSessionData) return null;
    const counts = anomalyHistory.reduce((acc, item) => {
      acc[item.prediction] = (acc[item.prediction] || 0) + 1;
      return acc;
    }, {});
    return {
      total: anomalyHistory.length,
      counts,
      lastTime: anomalyHistory[0]?.time || null,
    };
  }, [hasSessionData, anomalyHistory]);

  const handleCSV = () => {
    generateCSV(anomalyHistory, chosenPatient);
  };

  const handlePDF = async () => {
    setIsExporting(true);
    try {
      // Không kèm ảnh chụp biểu đồ ECG ở trang này (chartElement: null) - generatePDF đã xử
      // lý an toàn khi thiếu, vì trang Xuất Báo Cáo có thể mở bất kỳ lúc nào, không chắc tab
      // "Theo Dõi Trực Tuyến" đang render biểu đồ để chụp. Muốn báo cáo kèm ảnh ECG, dùng nút
      // "Xuất báo cáo" ngay trên Dashboard trong lúc đang xem trực tiếp bệnh nhân đó.
      await generatePDF({ anomalyHistory, patient: chosenPatient, chartElement: null });
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div className="card" style={{ padding: '20px 30px' }}>
        <h2 style={{ margin: '0 0 5px 0', color: 'var(--text-main)', fontSize: '20px' }}>📄 Báo Cáo Lâm Sàng</h2>
        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '14px' }}>
          Tổng hợp các cảnh báo nhịp bất thường đã ghi nhận trong phiên theo dõi hiện tại của 1
          bệnh nhân — kèm thông tin bệnh nhân, thống kê phân loại nhịp và bảng sự kiện, xuất
          được dạng PDF hoặc CSV.
        </p>
      </div>

      <div className="card" style={{ padding: '20px 30px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <label style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-main)' }}>Bệnh nhân:</label>
          <select
            value={chosenId}
            onChange={(e) => setChosenId(e.target.value)}
            style={{ padding: '9px 12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-main)', fontSize: '13.5px', minWidth: '260px' }}
          >
            <option value="" disabled>-- Chọn bệnh nhân --</option>
            {patients.map(p => (
              <option key={p.id} value={p.id}>
                {p.name} · Giường {p.bedNumber}{p.id === selectedPatient?.id ? ' (đang theo dõi)' : ''}
              </option>
            ))}
          </select>
        </div>

        {!chosenPatient ? (
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)' }}>
            Chọn 1 bệnh nhân để xem trước thống kê và xuất báo cáo.
          </p>
        ) : !hasSessionData ? (
          <div style={{ padding: '14px 16px', borderRadius: '8px', backgroundColor: 'var(--bg-color)', border: '1px dashed var(--border-color)', fontSize: '13px', color: 'var(--text-muted)' }}>
            ⚠️ Chưa có dữ liệu phiên theo dõi cho bệnh nhân này trong trình duyệt hiện tại — hãy
            theo dõi bệnh nhân này ở tab "Theo Dõi Trực Tuyến" trước, sau đó quay lại đây để xuất
            báo cáo. Vẫn có thể xuất được, nhưng báo cáo sẽ không có cảnh báo/thống kê nào.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px' }}>
            <StatTile label="Tổng cảnh báo" value={stats.total} />
            <StatTile label="Cập nhật gần nhất" value={stats.lastTime || '—'} />
            {Object.entries(stats.counts).map(([label, count]) => (
              <StatTile key={label} label={label} value={`${count} sự kiện`} accent={label.includes('CẢNH BÁO')} />
            ))}
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handlePDF}
            disabled={!chosenPatient || isExporting}
            style={{
              padding: '10px 18px', backgroundColor: 'var(--primary)', color: 'white',
              border: 'none', borderRadius: '8px', fontWeight: '600', fontSize: '13.5px',
              cursor: (!chosenPatient || isExporting) ? 'not-allowed' : 'pointer',
              opacity: (!chosenPatient || isExporting) ? 0.6 : 1,
            }}
          >
            {isExporting ? '⏳ Đang tạo PDF...' : '📄 Xuất PDF'}
          </button>
          <button
            onClick={handleCSV}
            disabled={!chosenPatient}
            style={{
              padding: '10px 18px', backgroundColor: 'transparent', color: 'var(--primary)',
              border: '1px solid var(--primary)', borderRadius: '8px', fontWeight: '600', fontSize: '13.5px',
              cursor: !chosenPatient ? 'not-allowed' : 'pointer',
              opacity: !chosenPatient ? 0.6 : 1,
            }}
          >
            📊 Xuất CSV
          </button>
        </div>
      </div>
    </div>
  );
};

const StatTile = ({ label, value, accent }) => (
  <div style={{ padding: '12px 14px', borderRadius: '8px', backgroundColor: 'var(--bg-color)', border: '1px solid var(--border-color)' }}>
    <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', marginBottom: '4px' }}>{label}</div>
    <div style={{ fontSize: '16px', fontWeight: '700', color: accent ? 'var(--danger)' : 'var(--text-main)' }}>{value}</div>
  </div>
);

export default ReportExporter;
