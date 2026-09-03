import React from 'react';
import { usePatient } from '../../context/PatientContext';

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

const PatientCard = ({ patient, isActive, onSelect, onEdit, onDelete, latestPrediction }) => {
  const isDanger = latestPrediction && latestPrediction.includes('CẢNH BÁO');
  const isWarning = latestPrediction && latestPrediction.includes('CẢNH BÁO') && !isDanger;

  const statusColor = isActive
    ? (isDanger ? '#ef4444' : '#10b981')
    : '#475569';

  return (
    <div style={{
      backgroundColor: '#ffffff',
      border: `2px solid ${isActive ? (isDanger ? '#ef4444' : 'var(--primary)') : '#e2e8f0'}`,
      borderRadius: '10px',
      padding: '18px 20px',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      boxShadow: isActive ? '0 4px 14px rgba(37,99,235,0.15)' : '0 1px 3px rgba(0,0,0,0.06)',
      position: 'relative',
      overflow: 'hidden',
    }}
      onClick={() => onSelect(patient)}
    >
      {/* Status indicator stripe */}
      <div style={{
        position: 'absolute', top: 0, left: 0, width: '4px', height: '100%',
        backgroundColor: statusColor,
      }} />

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px', paddingLeft: '8px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
            <span style={{ fontSize: '11px', fontWeight: '700', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Giường {patient.bedNumber}
            </span>
            {isActive && (
              <span style={{ fontSize: '10px', fontWeight: '700', backgroundColor: '#eff6ff', color: 'var(--primary)', padding: '2px 7px', borderRadius: '4px' }}>
                ● ĐANG THEO DÕI
              </span>
            )}
          </div>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: '#0f172a' }}>
            {patient.name}
          </h3>
          <p style={{ margin: '2px 0 0', fontSize: '13px', color: '#64748b' }}>
            {patient.age} tuổi · {GENDER_LABEL[patient.gender] || patient.gender}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={e => { e.stopPropagation(); onEdit(patient); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '15px', color: '#94a3b8', padding: '4px' }}
            title="Sửa"
          >✏️</button>
          <button
            onClick={e => { e.stopPropagation(); onDelete(patient.id); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '15px', color: '#94a3b8', padding: '4px' }}
            title="Xóa"
          >🗑️</button>
        </div>
      </div>

      {/* Details */}
      <div style={{ paddingLeft: '8px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
        {patient.attendingDoctor && (
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            👨‍⚕️ {patient.attendingDoctor}
          </div>
        )}
        {patient.diagnosis && (
          <div style={{ fontSize: '12px', color: '#94a3b8', fontStyle: 'italic', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {patient.diagnosis}
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8' }}>Bản ghi:</span>
          <span style={{ fontSize: '12px', fontWeight: '600', color: '#475569', backgroundColor: '#f1f5f9', padding: '2px 7px', borderRadius: '4px' }}>
            MIT-BIH #{patient.activeRecordId}
          </span>
        </div>
      </div>

      {/* Live prediction badge nếu đang active */}
      {isActive && latestPrediction && (
        <div style={{
          marginTop: '12px', paddingLeft: '8px', paddingTop: '10px',
          borderTop: '1px solid #e2e8f0',
        }}>
          <span style={{
            fontSize: '12px', fontWeight: '700',
            color: isDanger ? '#ef4444' : '#10b981',
            backgroundColor: isDanger ? '#fef2f2' : '#ecfdf5',
            padding: '3px 9px', borderRadius: '5px',
            display: 'inline-block'
          }}>
            {isDanger ? '🔴' : '🟢'} {latestPrediction}
          </span>
        </div>
      )}
    </div>
  );
};

export default PatientCard;
