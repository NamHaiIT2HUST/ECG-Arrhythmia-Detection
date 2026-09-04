import React from 'react';
import { useAlarm } from '../../context/AlarmContext';

const Header = () => {
  return (
    <header style={{ 
      height: '65px', 
      minHeight: '65px', 
      backgroundColor: '#ffffff', 
      borderBottom: '1px solid var(--border-color)', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between', 
      padding: '0 25px', 
      zIndex: 5, 
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '18px', color: 'var(--text-main)', fontWeight: '600' }}>Hệ Thống Theo Dõi Trung Tâm</h1>
        <span style={{ 
          padding: '4px 10px', 
          backgroundColor: 'var(--success-bg)', 
          color: 'var(--success)', 
          borderRadius: '4px', 
          fontSize: '12px', 
          fontWeight: '600',
          border: '1px solid #a7f3d0'
        }}>
          ● Phiên bản 1.0.0
        </span>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-main)' }}>BS. Nguyễn Văn B</div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Khoa Tim Mạch</div>
          </div>
          <div style={{ width: '38px', height: '38px', borderRadius: '50%', backgroundColor: 'var(--primary-bg)', color: 'var(--primary)', border: '1px solid #bfdbfe', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '14px' }}>
            NB
          </div>
        </div>
            <AlarmControls />
      </div>
    </header>
  );
};

    const AlarmControls = () => {
      const { isMuted, snoozeCountdown, currentAlarmLevel, muteAlarm, unmuteAlarm } = useAlarm();

      const levelIcon = currentAlarmLevel >= 3 ? '🔴' : (currentAlarmLevel === 2 ? '🟡' : '🟢');
      const levelText = currentAlarmLevel >= 3 ? 'Cấp 3' : (currentAlarmLevel === 2 ? 'Cấp 2' : 'Bình thường');

      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ fontSize: 18 }}>{levelIcon}</div>
            <div style={{ fontSize: 12, color: currentAlarmLevel >=3 ? '#ef4444' : (currentAlarmLevel===2 ? '#f59e0b' : '#10b981'), fontWeight: 700 }}>{levelText}</div>
          </div>
          <div>
            {isMuted ? (
              <button onClick={unmuteAlarm} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#fff', cursor: 'pointer' }}>
                Bật âm {snoozeCountdown > 0 ? `(${snoozeCountdown}s)` : ''}
              </button>
            ) : (
              <button onClick={muteAlarm} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #cbd5e1', background: '#fff', cursor: 'pointer' }}>
                Tắt âm 2 phút
              </button>
            )}
          </div>
        </div>
      );
    };

export default Header;
