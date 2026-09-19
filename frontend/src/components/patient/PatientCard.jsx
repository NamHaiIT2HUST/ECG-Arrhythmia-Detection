import React, { useState } from 'react';
import { getAlarmLevel } from '../../constants/alarmLevels';

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

const PatientCard = ({ patient, isActive, onSelect, onEdit, onDelete, latestPrediction }) => {
  const [isHovered, setIsHovered] = useState(false);
  const alarmLevel = getAlarmLevel(latestPrediction).level;
  const isDanger = alarmLevel === 3;
  const isWarning = alarmLevel === 2;

  const statusColor = isActive
    ? (isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--success)')
    : 'var(--border-color)';

  // Chỉ hiện những dòng có dữ liệu thật - trước đây luôn hiện "Chưa gán bác sĩ phụ trách"/
  // "Chưa có chẩn đoán" trên MỌI card (kể cả 47/48 bệnh nhân demo không có 2 trường này),
  // khiến danh sách trông rối vì lặp lại cùng 1 dòng chữ xám vô nghĩa ở tất cả các card.
  const metaParts = [
    patient.age ? `${patient.age} tuổi` : null,
    GENDER_LABEL[patient.gender] || patient.gender || null,
  ].filter(Boolean);

  return (
    <div
      onClick={() => onSelect(patient)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        backgroundColor: 'var(--card-bg)',
        border: `1px solid ${isActive ? (isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--primary)') : 'var(--border-color)'}`,
        borderRadius: '10px',
        padding: '16px 18px',
        cursor: 'pointer',
        transition: 'border-color 0.15s ease, box-shadow 0.15s ease',
        boxShadow: isActive ? '0 4px 14px rgba(47,109,246,0.15)' : 'none',
        position: 'relative',
      }}
    >
      {/* Status indicator stripe */}
      <div style={{
        position: 'absolute', top: '10px', left: '0', bottom: '10px', width: '3px',
        borderRadius: '0 3px 3px 0',
        backgroundColor: statusColor,
      }} />

      {/* Header: giường + trạng thái ..... nút sửa/xóa (chỉ hiện rõ khi hover, đỡ rối mắt) */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px', paddingLeft: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', minWidth: 0 }}>
          <span style={{
            fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)',
            backgroundColor: 'var(--bg-color)', padding: '2px 8px', borderRadius: '999px',
            whiteSpace: 'nowrap',
          }}>
            Giường {patient.bedNumber || '—'}
          </span>
          {isActive && (
            <span style={{ fontSize: '10px', fontWeight: '700', color: statusColor, whiteSpace: 'nowrap' }}>
              ● ĐANG THEO DÕI
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '2px', flexShrink: 0, opacity: isHovered ? 1 : 0, transition: 'opacity 0.15s ease' }}>
          <button
            onClick={e => { e.stopPropagation(); onEdit(patient); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '14px', color: 'var(--text-muted)', padding: '4px' }}
            title="Sửa"
          >✏️</button>
          <button
            onClick={e => { e.stopPropagation(); onDelete(patient.id); }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '14px', color: 'var(--text-muted)', padding: '4px' }}
            title="Xóa"
          >🗑️</button>
        </div>
      </div>

      {/* Tên + tuổi/giới tính + bác sĩ (nếu có) trên 1-2 dòng gọn */}
      <div style={{ paddingLeft: '10px', marginTop: '8px' }}>
        <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '700', color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {patient.name || <span style={{ fontWeight: '500', fontStyle: 'italic', color: 'var(--text-muted)' }}>Chưa có tên bệnh nhân</span>}
        </h3>
        {(metaParts.length > 0 || patient.attendingDoctor) && (
          <p style={{ margin: '3px 0 0', fontSize: '12.5px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {metaParts.join(' · ')}
            {metaParts.length > 0 && patient.attendingDoctor ? ' · ' : ''}
            {patient.attendingDoctor ? `BS. ${patient.attendingDoctor}` : ''}
          </p>
        )}
        {patient.diagnosis && (
          <p style={{ margin: '4px 0 0', fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {patient.diagnosis}
          </p>
        )}
      </div>

      {/* Footer: bản ghi + (nếu active) chẩn đoán AI mới nhất, gộp 1 dòng cho gọn */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px',
        marginTop: '12px', paddingTop: '10px', paddingLeft: '10px',
        borderTop: '1px solid var(--border-color)',
      }}>
        <span style={{ fontSize: '11px', fontWeight: '600', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
          {patient.activeRecordId ? `MIT-BIH #${patient.activeRecordId}` : '— chưa gán bản ghi —'}
        </span>
        {isActive && latestPrediction && (
          <span style={{
            fontSize: '11px', fontWeight: '700',
            color: isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--success)',
            backgroundColor: isDanger ? 'var(--danger-bg)' : isWarning ? 'rgba(245,158,11,0.12)' : 'var(--success-bg)',
            padding: '2px 8px', borderRadius: '999px',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '55%',
          }}>
            {isDanger ? '🔴' : isWarning ? '🟡' : '🟢'} {latestPrediction}
          </span>
        )}
      </div>
    </div>
  );
};

export default PatientCard;
