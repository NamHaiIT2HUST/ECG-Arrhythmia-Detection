import React from 'react';

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

const InfoRow = ({ label, value }) => {
  if (!value) return null;
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', padding: '9px 0', borderBottom: '1px solid var(--border-color)' }}>
      <span style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ fontSize: '13px', color: 'var(--text-main)', fontWeight: '600', textAlign: 'right' }}>{value}</span>
    </div>
  );
};

// Xem thông tin bệnh nhân TRƯỚC khi bắt đầu stream ECG - trước đây bấm thẳng vào card là stream
// ngay lập tức, không có bước xem lại hồ sơ/xác nhận đúng người trước khi theo dõi (rủi ro lâm
// sàng: bấm nhầm card gần nhau trong danh sách 48 bệnh nhân là stream nhầm ca). Modal này chỉ
// hiển thị thông tin + hành động, không có ô nhập liệu (sửa hồ sơ vẫn dùng PatientForm riêng).
const PatientDetailModal = ({ patient, isActive, onClose, onStartMonitoring, onStopMonitoring, onEdit }) => {
  if (!patient) return null;

  return (
    <div
      style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}
      onClick={onClose}
    >
      <div
        style={{
          width: '440px', maxWidth: '92%', maxHeight: '88vh', overflowY: 'auto',
          backgroundColor: 'var(--card-bg)', borderRadius: '14px', padding: '26px',
          border: '1px solid var(--border-color)', boxShadow: '0 20px 60px rgba(0,0,0,0.45)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '46px', height: '46px', borderRadius: '12px', flexShrink: 0,
              backgroundColor: 'var(--primary-bg)', color: 'var(--primary)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '21px',
            }}>🧑‍⚕️</div>
            <div>
              <h2 style={{ margin: 0, fontSize: '17px', color: 'var(--text-main)' }}>{patient.name || 'Chưa có tên'}</h2>
              <div style={{ fontSize: '12.5px', color: 'var(--text-muted)' }}>Giường {patient.bedNumber || '—'}</div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '20px', cursor: 'pointer', lineHeight: 1 }}>✕</button>
        </div>

        {isActive && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 12px', borderRadius: '8px', backgroundColor: 'var(--success-bg)', border: '1px solid var(--success)', marginBottom: '16px' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--success)' }} />
            <span style={{ fontSize: '12.5px', color: 'var(--success)', fontWeight: '600' }}>Đang được theo dõi trên Dashboard</span>
          </div>
        )}

        <div style={{ marginBottom: '18px' }}>
          <InfoRow label="Tuổi" value={patient.age ? `${patient.age} tuổi` : null} />
          <InfoRow label="Giới tính" value={GENDER_LABEL[patient.gender] || patient.gender} />
          <InfoRow label="Bác sĩ phụ trách" value={patient.attendingDoctor ? `BS. ${patient.attendingDoctor}` : null} />
          <InfoRow label="Chẩn đoán/Ghi chú" value={patient.diagnosis} />
          <InfoRow label="Ngày nhập viện" value={patient.admissionDate} />
          <InfoRow label="Bản ghi ECG" value={patient.activeRecordId ? `MIT-BIH #${patient.activeRecordId}` : 'Chưa gán'} />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="button"
            onClick={() => onEdit(patient)}
            style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'transparent', color: 'var(--text-main)', fontWeight: '600', fontSize: '13.5px', cursor: 'pointer' }}
          >
            ✏️ Sửa hồ sơ
          </button>
          {isActive ? (
            <button
              type="button"
              onClick={onStopMonitoring}
              style={{ flex: 1, padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--danger)', background: 'transparent', color: 'var(--danger)', fontWeight: '700', fontSize: '13.5px', cursor: 'pointer' }}
            >
              ⏹ Dừng theo dõi
            </button>
          ) : (
            <button
              type="button"
              onClick={() => onStartMonitoring(patient)}
              disabled={!patient.activeRecordId}
              title={!patient.activeRecordId ? 'Bệnh nhân chưa gán bản ghi ECG' : undefined}
              style={{
                flex: 1, padding: '10px 16px', borderRadius: '8px', border: 'none',
                background: patient.activeRecordId ? 'var(--primary)' : 'var(--border-color)',
                color: 'white', fontWeight: '700', fontSize: '13.5px',
                cursor: patient.activeRecordId ? 'pointer' : 'not-allowed',
              }}
            >
              ▶ Bắt đầu theo dõi
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientDetailModal;
