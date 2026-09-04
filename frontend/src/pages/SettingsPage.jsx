import React, { useState, useEffect } from 'react';
import { useAlarm } from '../context/AlarmContext';

const SETTINGS_KEY = 'ecg_settings';

const defaultSettings = {
  wsUrl: 'ws://localhost:8000',
  theme: 'auto', // 'auto' | 'light' | 'dark'
  confidenceThreshold: 0, // 0-1 (0 = không lọc)
  notificationEnabled: false,
};

export const loadSettings = () => {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    const merged = raw ? { ...defaultSettings, ...JSON.parse(raw) } : defaultSettings;
    // Normalize wsUrl: remove trailing slash if present
    if (merged.wsUrl?.endsWith('/')) merged.wsUrl = merged.wsUrl.replace(/\/+$/, '');
    return merged;
  } catch {
    return defaultSettings;
  }
};

const saveSettings = (settings) => {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
};

// Apply theme to <html> element
const applyTheme = (theme) => {
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)')?.matches;
  const isDark = theme === 'dark' || (theme === 'auto' && prefersDark);
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
};

const sectionStyle = {
  backgroundColor: 'var(--card-bg)',
  border: '1px solid var(--border-color)',
  borderRadius: '10px',
  padding: '24px',
  display: 'flex',
  flexDirection: 'column',
  gap: '20px',
};

const labelStyle = {
  fontSize: '14px',
  fontWeight: '600',
  color: 'var(--text-main)',
  marginBottom: '6px',
  display: 'block',
};

const descStyle = {
  fontSize: '12px',
  color: 'var(--text-muted)',
  marginTop: '4px',
};

const inputStyle = {
  padding: '9px 13px',
  border: '1px solid var(--border-color)',
  borderRadius: '6px',
  backgroundColor: 'var(--card-bg)',
  color: 'var(--text-main)',
  fontSize: '14px',
  outline: 'none',
  width: '100%',
  boxSizing: 'border-box',
};

const SettingsPage = () => {
  const [settings, setSettings] = useState(loadSettings);
  const [saved, setSaved] = useState(false);
  const [notifStatus, setNotifStatus] = useState(() => (typeof Notification !== 'undefined' ? Notification.permission : 'default'));
  const { muteAlarm, unmuteAlarm, isMuted, snoozeCountdown } = useAlarm();

  // Apply theme khi settings thay đổi
  useEffect(() => {
    applyTheme(settings.theme);
  }, [settings.theme]);

  // Theo dõi theme auto theo system preference
  useEffect(() => {
    if (settings.theme !== 'auto') return;
    const mq = window.matchMedia?.('(prefers-color-scheme: dark)');
    if (!mq) return;
    const handler = () => applyTheme('auto');
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [settings.theme]);

  const update = (key, value) => setSettings(prev => ({ ...prev, [key]: value }));

  const handleSave = () => {
    saveSettings(settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    setSettings(defaultSettings);
    saveSettings(defaultSettings);
    applyTheme(defaultSettings.theme);
  };

  const requestNotification = async () => {
    if (!('Notification' in window)) {
      alert('Trình duyệt này không hỗ trợ Push Notification.');
      return;
    }
    const permission = await Notification.requestPermission();
    setNotifStatus(permission);
    if (permission === 'granted') {
      update('notificationEnabled', true);
      saveSettings({ ...settings, notificationEnabled: true });
      new Notification('✅ Đã bật thông báo ECG', {
        body: 'Bạn sẽ nhận được cảnh báo khi phát hiện nhịp tim khẩn cấp.',
      });
    }
  };

  return (
    <div style={{ padding: '25px', maxWidth: '1100px', width: '100%', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ margin: '0 0 4px', color: 'var(--text-main)', fontSize: '22px', fontWeight: '700' }}>
          ⚙️ Cài Đặt Hệ Thống
        </h2>
        <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)' }}>
          Cấu hình được lưu tự động vào trình duyệt và áp dụng ngay.
        </p>
      </div>

      {/* Section 1: Kết nối */}
      <div style={{ ...sectionStyle, width: '100%' }}>
        <h3 style={{ margin: '0 0 4px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          🔌 Kết nối Backend
        </h3>
        <div>
          <label style={labelStyle}>Địa chỉ WebSocket Server</label>
          <input
            id="ws-url-input"
            type="text"
            style={inputStyle}
            value={settings.wsUrl}
            onChange={e => update('wsUrl', e.target.value)}
            placeholder="ws://localhost:8000"
          />
          <p style={descStyle}>
            Dashboard sẽ kết nối WebSocket tới địa chỉ này. Mặc định: <code>ws://localhost:8000</code>. Đổi khi deploy lên server khác.
          </p>
        </div>
      </div>

      {/* Section 2: Giao diện */}
      <div style={{ ...sectionStyle, width: '100%' }}>
        <h3 style={{ margin: '0 0 4px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          🎨 Giao diện
        </h3>
        <div>
          <label style={labelStyle}>Chế độ màu</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            {[
              { value: 'auto', label: '🔄 Tự động (theo hệ thống)' },
              { value: 'light', label: '☀️ Sáng' },
              { value: 'dark', label: '🌙 Tối' },
            ].map(opt => (
              <label key={opt.value} style={{
                display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer',
                padding: '8px 14px', borderRadius: '7px', fontSize: '13px',
                border: `2px solid ${settings.theme === opt.value ? 'var(--primary)' : 'var(--border-color)'}`,
                backgroundColor: settings.theme === opt.value ? 'var(--primary-bg)' : 'transparent',
                color: settings.theme === opt.value ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: settings.theme === opt.value ? '600' : '400',
                transition: 'all 0.15s ease',
              }}>
                <input
                  type="radio"
                  name="theme"
                  value={opt.value}
                  checked={settings.theme === opt.value}
                  onChange={() => update('theme', opt.value)}
                  style={{ display: 'none' }}
                />
                {opt.label}
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Section 3: Cảnh báo AI */}
      <div style={{ ...sectionStyle, width: '100%' }}>
        <h3 style={{ margin: '0 0 4px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          🎯 Độ nhạy cảnh báo AI
        </h3>
        <div>
          <label style={labelStyle}>
            Ngưỡng Confidence tối thiểu: <strong style={{ color: 'var(--primary)' }}>
              {settings.confidenceThreshold === 0 ? 'Không lọc' : `${Math.round(settings.confidenceThreshold * 100)}%`}
            </strong>
          </label>
          <input
            id="confidence-threshold-slider"
            type="range"
            min="0"
            max="0.95"
            step="0.05"
            value={settings.confidenceThreshold}
            onChange={e => update('confidenceThreshold', parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--primary)' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)' }}>
            <span>Không lọc (0%)</span>
            <span>Chỉ cảnh báo khi AI rất chắc (95%)</span>
          </div>
          <p style={descStyle}>
            Chỉ kích hoạt alarm khi AI dự đoán với confidence ≥ ngưỡng này. Field <code>confidence</code> trong payload WS. Ngưỡng 0 = không lọc (hành vi mặc định).
          </p>
        </div>

        {/* Mute/Snooze */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <label style={labelStyle}>Trạng thái âm thanh cảnh báo</label>
          {isMuted ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '14px', color: '#f59e0b', fontWeight: '600' }}>
                🔇 Đang tắt tiếng — còn {Math.floor(snoozeCountdown / 60)}:{String(snoozeCountdown % 60).padStart(2, '0')} phút
              </span>
              <button
                id="unmute-btn"
                onClick={unmuteAlarm}
                style={{
                  padding: '6px 14px', backgroundColor: '#10b981', color: 'white',
                  border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600'
                }}
              >
                🔔 Bật lại ngay
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '14px', color: '#10b981' }}>🔔 Đang bật</span>
              <button
                id="mute-btn"
                onClick={muteAlarm}
                style={{
                  padding: '6px 14px', backgroundColor: '#f59e0b', color: 'white',
                  border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600'
                }}
              >
                🔇 Tắt tiếng 2 phút
              </button>
            </div>
          )}
          <p style={descStyle}>Âm thanh sẽ tự bật lại sau 2 phút (chuẩn y tế IEC 60601-1-8 — không cho tắt vĩnh viễn).</p>
        </div>
      </div>

      {/* Section 4: Thông báo */}
      <div style={{ ...sectionStyle, width: '100%' }}>
        <h3 style={{ margin: '0 0 4px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          🔔 Thông báo đẩy (Browser Push)
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <p style={{ margin: '0 0 4px', fontSize: '14px', color: 'var(--text-main)' }}>
              Trạng thái quyền: <strong style={{
                color: notifStatus === 'granted' ? '#10b981' : notifStatus === 'denied' ? '#ef4444' : '#f59e0b'
              }}>
                {notifStatus === 'granted' ? '✅ Đã cấp quyền' : notifStatus === 'denied' ? '❌ Bị từ chối' : '⏳ Chưa xin'}
              </strong>
            </p>
            <p style={descStyle}>
              Thông báo đẩy sẽ xuất hiện ngay cả khi tab không được focus. Chỉ kích hoạt cho cảnh báo mức 3 (Khẩn cấp).
            </p>
          </div>
          {notifStatus !== 'granted' && notifStatus !== 'denied' && (
            <button
              id="request-notification-btn"
              onClick={requestNotification}
              style={{
                padding: '10px 18px', backgroundColor: 'var(--primary)', color: 'white',
                border: 'none', borderRadius: '7px', fontWeight: '600', cursor: 'pointer',
                whiteSpace: 'nowrap', marginLeft: '16px',
              }}
            >
              Cho phép thông báo
            </button>
          )}
          {notifStatus === 'denied' && (
            <p style={{ ...descStyle, color: '#ef4444', marginLeft: '16px', whiteSpace: 'nowrap' }}>
              Vào Settings trình duyệt để cấp lại.
            </p>
          )}
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
        <button
          onClick={handleReset}
          style={{
            padding: '10px 20px', background: 'transparent', color: 'var(--text-muted)',
            border: '1px solid var(--border-color)', borderRadius: '7px', cursor: 'pointer', fontWeight: '500'
          }}
        >
          Đặt lại mặc định
        </button>
        <button
          id="save-settings-btn"
          onClick={handleSave}
          style={{
            padding: '10px 24px', backgroundColor: saved ? '#10b981' : 'var(--primary)',
            color: 'white', border: 'none', borderRadius: '7px', cursor: 'pointer', fontWeight: '600',
            transition: 'background-color 0.2s ease',
          }}
        >
          {saved ? '✅ Đã lưu!' : '💾 Lưu cài đặt'}
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;
