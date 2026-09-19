import React from 'react';

const StatCards = ({ latestPrediction, currentAlarmLevel = 0, currentAlarmLabel, bpm, hrv_sdnn, hrv_rmssd, confidence, afibSuspected, afibScore, tachycardiaSuspected }) => {
  // Dùng chung currentAlarmLevel/currentAlarmLabel từ AlarmContext (nguồn duy nhất quyết định
  // còi/màu, xem AlarmContext.jsx:triggerAlarm) thay vì tự tính lại isDanger từ latestPrediction
  // + afibSuspected/tachycardiaSuspected - trước đây 2 nguồn lệch nhau khiến card tô ĐỎ (do
  // AFib/tachycardia) nhưng chữ chính vẫn in "BÌNH THƯỜNG" của riêng nhãn AAMI từng nhịp, nhìn
  // mâu thuẫn và gây hoang mang cho bác sĩ.
  const isDanger = currentAlarmLevel === 3;
  const isWarning = currentAlarmLevel === 2;
  const aiColor = isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--text-main)';

  // Độ trễ xử lý (E2E/AI) đã CHUYỂN sang hiển thị dạng chỉ báo nhỏ trong toolbar
  // (DashboardPage.jsx) thay vì 1 thẻ riêng ở đây - đây là số liệu hiệu năng HỆ THỐNG, không
  // phải thông tin lâm sàng về bệnh nhân, nên không nên đứng ngang hàng thị giác với BPM/HRV/
  // chẩn đoán AI trên hàng chỉ số chính mà bác sĩ nhìn vào để ra quyết định.
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '15px' }}>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : isWarning ? 'rgba(245,158,11,0.08)' : 'var(--card-bg)',
        borderLeft: `4px solid ${isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--primary)'}`,
        gridColumn: 'span 2'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🤖 Phân Tích AI
        </h3>
        <p style={{ margin: 0, fontSize: '20px', fontWeight: '700', color: aiColor }}>
          {currentAlarmLabel || latestPrediction}
        </p>
        {/* Phân loại hình dạng của đúng nhịp vừa ghi nhận - luôn hiện, kể cả khi tiêu đề trên
            đang phản ánh 1 điều kiện khác (AFib/tachycardia) chứ không phải phân loại nhịp đơn
            lẻ này. Bỏ nhãn "(AAMI)" và mã chữ cái viết tắt (thuật ngữ phân loại học thuật, không
            cần thiết với bác sĩ) - chỉ giữ đúng tên lâm sàng. */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>Nhịp vừa ghi nhận:</span>
          <span style={{ fontSize: '11.5px', color: 'var(--text-main)', fontWeight: '600' }}>{latestPrediction}</span>
        </div>
        {Boolean(afibSuspected) && (
          <div style={{ marginTop: '4px', fontSize: '12px', fontWeight: '700', color: 'var(--danger)', background: 'var(--danger-bg)', borderRadius: '999px', padding: '4px 8px', display: 'inline-flex', alignItems: 'center', gap: '4px', width: 'fit-content' }}>
            ⚠️ Nghi ngờ Rung Nhĩ (score {Number(afibScore ?? 0).toFixed(2)})
          </div>
        )}
        {Boolean(tachycardiaSuspected) && (
          <div style={{ marginTop: '4px', fontSize: '12px', fontWeight: '700', color: 'var(--warning)', background: 'var(--warning-bg)', borderRadius: '999px', padding: '4px 8px', display: 'inline-flex', alignItems: 'center', gap: '4px', width: 'fit-content' }}>
            ⚡ Nhịp Tim Nhanh Bất Thường (≥100 bpm)
          </div>
        )}
      </div>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid var(--success)'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          💓 Nhịp tim (BPM)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {bpm ?? '--'}
          </p>
        </div>
        {/* RR interval = 60000/BPM - suy ra trực tiếp từ BPM đã đo, không phải số liệu mới */}
        <p style={{ margin: 0, fontSize: '11.5px', color: 'var(--text-muted)' }}>
          RR: {bpm ? `${Math.round(60000 / bpm)} ms` : '--'}
        </p>
      </div>

      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid var(--accent-info)'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          📈 HRV (SDNN)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {hrv_sdnn != null ? hrv_sdnn.toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>ms</span>
        </div>
        <p style={{ margin: 0, fontSize: '11.5px', color: 'var(--text-muted)' }}>
          RMSSD: {hrv_rmssd != null ? `${hrv_rmssd.toFixed(1)} ms` : '--'}
        </p>
      </div>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid var(--warning)'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🎯 Độ tin cậy AI
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {confidence != null ? (confidence * 100).toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>%</span>
        </div>
      </div>

    </div>
  );
};

export default StatCards;
