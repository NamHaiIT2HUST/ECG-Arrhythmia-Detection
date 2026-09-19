import React from 'react';
import { getAlarmLevel } from '../../constants/alarmLevels';

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

const PatientCard = ({ patient, isActive, onSelect, onEdit, onDelete, latestPrediction }) => {
  const alarmLevel = getAlarmLevel(latestPrediction).level;
  const isDanger = alarmLevel === 3;
  const isWarning = alarmLevel === 2;

  const statusColor = isActive
    ? (isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--success)')
    : 'var(--border-color)';

  const hasName = Boolean(patient.name);
  const hasAge = Boolean(patient.age) || Boolean(patient.gender);

  return (
    <div style={{
      backgroundColor: 'var(--card-bg)',
      border: `2px solid ${isActive ? (isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--primary)') : 'var(--border-color)'}`,
      borderRadius: '10px',
      padding: '18px 20px 18px 24px',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      boxShadow: isActive ? '0 4px 14px rgba(47,109,246,0.15)' : '0 1px 3px rgba(0,0,0,0.06)',
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '10px' }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', marginBottom: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Giường {patient.bedNumber || '—'}
            </span>
            {isActive && (
              <span style={{ fontSize: '10px', fontWeight: '700', backgroundColor: 'var(--primary-bg)', color: 'var(--primary)', padding: '2px 7px', borderRadius: '4px', whiteSpace: 'nowrap' }}>
                ● ĐANG THEO DÕI
              </span>
            )}
          </div>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: 'var(--text-main)' }}>
            {hasName ? patient.name : <span style={{ fontWeight: '500', fontStyle: 'italic', color: 'var(--text-muted)' }}>Chưa có tên bệnh nhân</span>}
          </h3>
          {hasAge && (
            <p style={{ margin: '2px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
              {patient.age ? `${patient.age} tuổi` : ''}{patient.age && patient.gender ? ' · ' : ''}{GENDER_LABEL[patient.gender] || patient.gender || ''}
            </p>
          )}
        </div>
        <div style={{ display: 'flex', gap: '4px', flexShrink: 0 }}>
          <button
            onClick={e => { e.stopPropagation(); onEdit(patient); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '15px', color: 'var(--text-muted)', padding: '4px' }}
            title="Sửa"
          >✏️</button>
          <button
            onClick={e => { e.stopPropagation(); onDelete(patient.id); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '15px', color: 'var(--text-muted)', padding: '4px' }}
            title="Xóa"
          >🗑️</button>
        </div>
      </div>

      {/* Details */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          👨‍⚕️ {patient.attendingDoctor || <span style={{ fontStyle: 'italic' }}>Chưa gán bác sĩ phụ trách</span>}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {patient.diagnosis || 'Chưa có chẩn đoán/tiền sử'}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Bản ghi:</span>
          <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)', backgroundColor: 'var(--bg-color)', padding: '2px 7px', borderRadius: '4px' }}>
            {patient.activeRecordId ? `MIT-BIH #${patient.activeRecordId}` : 'Chưa gán bản ghi'}
          </span>
        </div>
      </div>

      {/* Live prediction badge nếu đang active */}
      {isActive && latestPrediction && (
        <div style={{
          marginTop: '12px', paddingTop: '10px',
          borderTop: '1px solid var(--border-color)',
        }}>
          <span style={{
            fontSize: '12px', fontWeight: '700',
            color: isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--success)',
            backgroundColor: isDanger ? 'var(--danger-bg)' : isWarning ? 'rgba(245,158,11,0.12)' : 'var(--success-bg)',
            padding: '3px 9px', borderRadius: '5px',
            display: 'inline-block'
          }}>
            {isDanger ? '🔴' : isWarning ? '🟡' : '🟢'} {latestPrediction}
          </span>
        </div>
      )}
    </div>
  );
};

export default PatientCard;
