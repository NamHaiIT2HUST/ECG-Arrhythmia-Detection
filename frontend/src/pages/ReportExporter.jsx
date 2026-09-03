import React from 'react';
import { usePatient } from '../context/PatientContext';

const downloadCSV = (filename, rows) => {
  const csv = [Object.keys(rows[0]).join(','), ...rows.map(r => Object.values(r).map(v => `"${String(v).replace(/"/g,'""')}"`).join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

const printReport = (html) => {
  const w = window.open('', '_blank', 'noopener,width=800,height=600');
  if (!w) return alert('Không thể mở cửa sổ in');
  w.document.write('<html><head><title>Báo cáo ECG</title>');
  w.document.write('<style>body{font-family:Inter, sans-serif;padding:20px;} table{width:100%;border-collapse:collapse;} th,td{border:1px solid #ddd;padding:8px;text-align:left;} th{background:#f3f4f6;}</style>');
  w.document.write('</head><body>');
  w.document.write(html);
  w.document.write('</body></html>');
  w.document.close();
  w.focus();
  setTimeout(() => w.print(), 300);
};

const ReportExporter = () => {
  const { patients } = usePatient();

  const handleExportCSV = () => {
    if (!patients || patients.length === 0) return alert('Không có bệnh nhân để xuất báo cáo.');
    const rows = patients.map(p => ({ id: p.id || '', name: p.name || '', bed: p.bedNumber || '', activeRecord: p.activeRecordId || '' }));
    downloadCSV('ecg_patients_report.csv', rows);
  };

  const handlePrint = () => {
    if (!patients || patients.length === 0) return alert('Không có bệnh nhân để in.');
    const html = `
      <h1>Báo cáo Bệnh Nhân — NEURO-ECG</h1>
      <p>Thời gian: ${new Date().toLocaleString()}</p>
      <table>
        <thead><tr><th>#</th><th>Họ tên</th><th>Bed</th><th>Active Record</th></tr></thead>
        <tbody>
          ${patients.map((p, i) => `<tr><td>${i+1}</td><td>${p.name||''}</td><td>${p.bedNumber||''}</td><td>${p.activeRecordId||''}</td></tr>`).join('')}
        </tbody>
      </table>
    `;
    printReport(html);
  };

  return (
    <div style={{ padding: '25px' }}>
      <div className="card" style={{ padding: 20 }}>
        <h2 style={{ margin: 0, color: 'var(--text-main)' }}>📄 Xuất Báo Cáo</h2>
        <p style={{ color: 'var(--text-muted)' }}>Xuất danh sách bệnh nhân hiện tại sang CSV hoặc in báo cáo PDF thông qua trình duyệt.</p>

        <div style={{ marginTop: 18, display: 'flex', gap: 12 }}>
          <button onClick={handleExportCSV} style={{ padding: '10px 16px', backgroundColor: 'var(--primary)', color: 'white', border: 'none', borderRadius: 8 }}>📥 Xuất CSV</button>
          <button onClick={handlePrint} style={{ padding: '10px 16px', backgroundColor: 'var(--primary-hover)', color: 'white', border: 'none', borderRadius: 8 }}>🖨️ In / PDF</button>
        </div>
      </div>
    </div>
  );
};

export default ReportExporter;
