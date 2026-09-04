/**
 * reportGenerator.js — Xuất báo cáo y tế PDF và CSV
 * Dùng jspdf + html2canvas cho PDF, Blob thuần cho CSV.
 */

/**
 * Xuất CSV từ lịch sử cảnh báo
 * @param {Array} anomalyHistory - từ AnomalyContext
 * @param {object} patient - từ PatientContext (nullable)
 */
export const generateCSV = (anomalyHistory, patient = null) => {
  const headers = ['Thời gian', 'Chẩn đoán AI', 'Độ tin cậy (%)', 'Độ trễ (ms)'];
  const rows = anomalyHistory.map(item => [
    item.time || '',
    item.prediction || '',
    item.confidence != null ? (item.confidence * 100).toFixed(1) : '',
    item.latency?.toFixed(1) || '',
  ]);

  const csvContent = [
    // Header bệnh nhân nếu có
    patient ? `# Bệnh nhân: ${patient.name} | Giường: ${patient.bedNumber} | Ngày: ${new Date().toLocaleDateString('vi-VN')}` : `# Báo cáo ECG — ${new Date().toLocaleDateString('vi-VN')}`,
    '',
    headers.join(','),
    ...rows.map(r => r.join(',')),
  ].join('\n');

  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' }); // BOM UTF-8 để Excel đọc đúng tiếng Việt
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ECG_report_${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

/**
 * Xuất PDF báo cáo y tế
 * @param {object} options
 * @param {Array} options.anomalyHistory - từ AnomalyContext
 * @param {object} options.patient - từ PatientContext (nullable)
 * @param {HTMLElement} options.chartElement - DOM element để html2canvas chụp
 */
export const generatePDF = async ({ anomalyHistory, patient, chartElement }) => {
  // Import lazy để không làm nặng bundle khi chưa dùng
  const { jsPDF } = await import('jspdf');
  const { default: html2canvas } = await import('html2canvas');

  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 15;
  let y = margin;

  // ---- HEADER ----
  doc.setFillColor(37, 99, 235);
  doc.rect(0, 0, pageWidth, 28, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.text('BÁO CÁO ECG — HỆ THỐNG NEURO-ECG', margin, 12);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.text(`Xuất lúc: ${new Date().toLocaleString('vi-VN')}`, margin, 20);
  doc.text(`Tổng cảnh báo: ${anomalyHistory.length}`, pageWidth - margin - 40, 20);
  y = 35;

  // ---- THÔNG TIN BỆNH NHÂN ----
  doc.setTextColor(15, 23, 42);
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.text('THÔNG TIN BỆNH NHÂN', margin, y);
  y += 6;
  doc.setDrawColor(226, 232, 240);
  doc.line(margin, y, pageWidth - margin, y);
  y += 5;
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(71, 85, 105);

  if (patient) {
    const info = [
      [`Họ tên:`, patient.name || '—'],
      [`Tuổi / Giới:`, `${patient.age || '—'} / ${patient.gender || '—'}`],
      [`Số giường:`, patient.bedNumber || '—'],
      [`Bác sĩ phụ trách:`, patient.attendingDoctor || '—'],
      [`Tiền sử bệnh:`, patient.diagnosis || '—'],
      [`Ngày nhập viện:`, patient.admissionDate || '—'],
    ];
    info.forEach(([label, value]) => {
      doc.setFont('helvetica', 'bold');
      doc.text(label, margin, y);
      doc.setFont('helvetica', 'normal');
      doc.text(String(value), margin + 42, y);
      y += 6;
    });
  } else {
    doc.text('Chưa chọn bệnh nhân cụ thể (xem tab Hồ Sơ Bệnh Nhân)', margin, y);
    y += 6;
  }
  y += 4;

  // ---- SNAPSHOT ECG CHART ----
  if (chartElement) {
    try {
      const canvas = await html2canvas(chartElement, {
        backgroundColor: '#ffffff',
        scale: 1.5,
        logging: false,
        useCORS: true,
      });
      const imgData = canvas.toDataURL('image/jpeg', 0.85);
      const imgWidth = pageWidth - margin * 2;
      const imgHeight = (canvas.height / canvas.width) * imgWidth;

      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(15, 23, 42);
      doc.text('BIỂU ĐỒ ECG THỜI GIAN THỰC (SNAPSHOT)', margin, y);
      y += 4;
      doc.addImage(imgData, 'JPEG', margin, y, imgWidth, Math.min(imgHeight, 80));
      y += Math.min(imgHeight, 80) + 8;
    } catch (err) {
      console.warn('Không thể chụp chart:', err);
    }
  }

  // ---- BẢNG THỐNG KÊ ----
  if (y > pageHeight - 60) { doc.addPage(); y = margin; }
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(15, 23, 42);
  doc.text('THỐNG KÊ PHÂN LOẠI NHỊP', margin, y);
  y += 6;
  doc.setDrawColor(226, 232, 240);
  doc.line(margin, y, pageWidth - margin, y);
  y += 4;

  // Tính thống kê
  const counts = anomalyHistory.reduce((acc, item) => {
    acc[item.prediction] = (acc[item.prediction] || 0) + 1;
    return acc;
  }, {});

  const total = anomalyHistory.length;
  doc.setFontSize(9);
  Object.entries(counts).forEach(([label, count]) => {
    const pct = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0';
    const isDanger = label.includes('CẢNH BÁO');
    doc.setTextColor(isDanger ? 220 : 16, isDanger ? 38 : 185, isDanger ? 38 : 129);
    doc.setFont('helvetica', 'bold');
    doc.text(label, margin, y);
    doc.setTextColor(71, 85, 105);
    doc.setFont('helvetica', 'normal');
    doc.text(`${count} sự kiện (${pct}%)`, margin + 90, y);
    y += 6;
  });

  if (total === 0) {
    doc.setTextColor(100, 116, 139);
    doc.setFont('helvetica', 'italic');
    doc.text('Chưa có cảnh báo nào được ghi nhận trong phiên này.', margin, y);
    y += 6;
  }
  y += 4;

  // ---- DANH SÁCH SỰ KIỆN ----
  if (anomalyHistory.length > 0) {
    if (y > pageHeight - 40) { doc.addPage(); y = margin; }
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(15, 23, 42);
    doc.text(`DANH SÁCH SỰ KIỆN BẤT THƯỜNG (${Math.min(anomalyHistory.length, 30)} gần nhất)`, margin, y);
    y += 6;
    doc.line(margin, y, pageWidth - margin, y);
    y += 5;

    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(100, 116, 139);
    doc.text('Thời gian', margin, y);
    doc.text('Chẩn đoán', margin + 25, y);
    doc.text('Độ tin cậy', margin + 105, y);
    doc.text('Độ trễ (ms)', margin + 130, y);
    y += 5;
    doc.setFont('helvetica', 'normal');

    anomalyHistory.slice(0, 30).forEach(item => {
      if (y > pageHeight - 15) { doc.addPage(); y = margin + 5; }
      const isDanger = item.prediction?.includes('CẢNH BÁO');
      doc.setTextColor(isDanger ? 239 : 100, isDanger ? 68 : 116, isDanger ? 68 : 139);
      doc.text(item.time || '—', margin, y);
      doc.text(item.prediction?.slice(0, 42) || '—', margin + 25, y);
      doc.setTextColor(71, 85, 105);
      doc.text(item.confidence != null ? `${(item.confidence * 100).toFixed(1)}%` : '—', margin + 105, y);
      doc.text(item.latency != null ? `${item.latency.toFixed(1)}` : '—', margin + 130, y);
      y += 5;
    });
  }

  // ---- FOOTER ----
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(148, 163, 184);
    doc.setFont('helvetica', 'normal');
    doc.text(
      'Tài liệu này chỉ có giá trị tham khảo hỗ trợ lâm sàng. Không thay thế chẩn đoán của bác sĩ có chuyên môn.',
      margin, pageHeight - 8
    );
    doc.text(`Trang ${i}/${totalPages}`, pageWidth - margin - 15, pageHeight - 8);
  }

  doc.save(`ECG_report_${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.pdf`);
};
