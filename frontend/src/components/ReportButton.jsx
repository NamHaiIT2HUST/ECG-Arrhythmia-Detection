import React, { useState } from 'react';
import { useAnomaly } from '../context/AnomalyContext';
import { usePatient } from '../context/PatientContext';
import { generateCSV, generatePDF } from '../utils/reportGenerator';

const ReportButton = ({ chartElementRef }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const { anomalyHistory } = useAnomaly();
  const { activePatient } = usePatient();

  const handleCSV = () => {
    setIsOpen(false);
    generateCSV(anomalyHistory, activePatient);
  };

  const handlePDF = async () => {
    setIsOpen(false);
    setLoading(true);
    try {
      await generatePDF({
        anomalyHistory,
        patient: activePatient,
        chartElement: chartElementRef?.current || null,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        id="report-export-btn"
        onClick={() => setIsOpen(prev => !prev)}
        disabled={loading}
        style={{
          padding: '7px 14px',
          backgroundColor: 'transparent',
          color: 'var(--text-main)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          fontWeight: '600',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.6 : 1,
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '7px',
        }}
        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.backgroundColor = 'var(--bg-color)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
      >
        {loading ? '⏳ Đang tạo...' : '📄 Xuất báo cáo'}
      </button>

      {isOpen && (
        <>
          {/* Overlay đóng dropdown khi click ngoài */}
          <div
            style={{ position: 'fixed', inset: 0, zIndex: 99 }}
            onClick={() => setIsOpen(false)}
          />
          <div style={{
            position: 'absolute', top: '110%', right: 0,
            backgroundColor: 'var(--card-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.25)',
            zIndex: 100,
            minWidth: '180px',
            overflow: 'hidden',
          }}>
            <button
              id="export-pdf-btn"
              onClick={handlePDF}
              style={{
                width: '100%', padding: '12px 16px', background: 'none',
                border: 'none', textAlign: 'left', cursor: 'pointer',
                fontSize: '14px', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px',
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = 'var(--bg-color)'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              📄 Xuất PDF
              <span style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--text-muted)' }}>+ Snapshot ECG</span>
            </button>
            <div style={{ height: '1px', backgroundColor: 'var(--border-color)' }} />
            <button
              id="export-csv-btn"
              onClick={handleCSV}
              style={{
                width: '100%', padding: '12px 16px', background: 'none',
                border: 'none', textAlign: 'left', cursor: 'pointer',
                fontSize: '14px', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px',
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = 'var(--bg-color)'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              📊 Xuất CSV
              <span style={{ marginLeft: 'auto', fontSize: '11px', color: 'var(--text-muted)' }}>Mở Excel được</span>
            </button>
            {anomalyHistory.length === 0 && (
              <div style={{ padding: '8px 16px', fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                Chưa có dữ liệu cảnh báo.
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ReportButton;
