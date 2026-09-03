import React, { useState, useRef } from 'react';
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
          padding: '8px 16px',
          backgroundColor: loading ? '#475569' : '#10b981',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          fontWeight: '600',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
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
            backgroundColor: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
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
                fontSize: '14px', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px',
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = '#f8fafc'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              📄 Xuất PDF
              <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#94a3b8' }}>+ Snapshot ECG</span>
            </button>
            <div style={{ height: '1px', backgroundColor: '#f1f5f9' }} />
            <button
              id="export-csv-btn"
              onClick={handleCSV}
              style={{
                width: '100%', padding: '12px 16px', background: 'none',
                border: 'none', textAlign: 'left', cursor: 'pointer',
                fontSize: '14px', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px',
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = '#f8fafc'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = 'transparent'}
            >
              📊 Xuất CSV
              <span style={{ marginLeft: 'auto', fontSize: '11px', color: '#94a3b8' }}>Mở Excel được</span>
            </button>
            {anomalyHistory.length === 0 && (
              <div style={{ padding: '8px 16px', fontSize: '12px', color: '#94a3b8', fontStyle: 'italic' }}>
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
