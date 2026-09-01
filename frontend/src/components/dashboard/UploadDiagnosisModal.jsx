import React, { useState, useRef } from 'react';
import api from '../../api/axios';

const UploadDiagnosisModal = ({ isOpen, onClose }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setReport(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Vui lòng chọn file CSV.');
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Gọi API POST upload file (theo tài liệu: /api/diagnosis/upload-ecg)
      const response = await api.post('/api/diagnosis/upload-ecg?fs=360', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setReport(response.data);
    } catch (err) {
      console.error(err);
      setError('Đã xảy ra lỗi khi phân tích bản ghi. Kiểm tra lại định dạng file (CSV).');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setReport(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex',
      alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div className="card" style={{ 
        width: '600px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto',
        padding: '25px', backgroundColor: 'var(--bg-color)' 
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, color: 'var(--text-main)', fontSize: '20px' }}>Chẩn Đoán Từ Bản Ghi (CSV)</h2>
          <button 
            onClick={handleClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '20px' }}
          >
            ✕
          </button>
        </div>

        {!report ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ border: '2px dashed #475569', borderRadius: '8px', padding: '30px', textAlign: 'center' }}>
              <input 
                type="file" 
                accept=".csv"
                onChange={handleFileChange} 
                ref={fileInputRef}
                style={{ display: 'none' }}
                id="csv-upload"
              />
              <label htmlFor="csv-upload" style={{ cursor: 'pointer', color: 'var(--primary)', fontWeight: '600' }}>
                {file ? file.name : 'Nhấn để chọn file CSV (MIT-BIH format)'}
              </label>
              <p style={{ margin: '10px 0 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
                Yêu cầu: File có dữ liệu biên độ (mV), 1 cột hoặc cột cuối cùng, mẫu &gt; 2s.
              </p>
            </div>
            
            {error && <div style={{ color: 'var(--danger)', fontSize: '14px' }}>{error}</div>}
            
            <button 
              onClick={handleUpload}
              disabled={loading || !file}
              style={{
                padding: '12px',
                backgroundColor: loading || !file ? '#475569' : 'var(--primary)',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: loading || !file ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Đang phân tích AI...' : 'Tải Lên & Chẩn Đoán'}
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ backgroundColor: 'var(--card-bg)', padding: '15px', borderRadius: '8px' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: 'var(--primary)' }}>Tóm tắt Phân tích</h3>
              <p style={{ margin: '5px 0', color: 'var(--text-main)' }}>{report.overall_assessment}</p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px' }}>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Thời lượng:</span> <strong>{report.duration_seconds.toFixed(1)} s</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Tổng số nhịp:</span> <strong>{report.total_beats}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>BPM (TB):</span> <strong>{report.bpm.avg?.toFixed(1) || '--'}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>HRV (SDNN):</span> <strong>{report.hrv.sdnn_ms?.toFixed(1) || '--'} ms</strong>
                </div>
              </div>
            </div>

            <div style={{ backgroundColor: 'var(--card-bg)', padding: '15px', borderRadius: '8px' }}>
              <h3 style={{ margin: '0 0 10px 0', fontSize: '16px', color: 'var(--text-main)' }}>Phân bố Nhịp tim</h3>
              {Object.entries(report.class_counts).map(([label, count]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px' }}>
                  <span style={{ color: label === 'BÌNH THƯỜNG' ? '#10b981' : 'var(--danger)' }}>{label}</span>
                  <span>{count} nhịp ({report.class_percentages[label]})</span>
                </div>
              ))}
            </div>

            <button 
              onClick={resetForm}
              style={{
                padding: '12px',
                backgroundColor: 'transparent',
                color: 'var(--primary)',
                border: '1px solid var(--primary)',
                borderRadius: '6px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              Chẩn đoán file khác
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadDiagnosisModal;
