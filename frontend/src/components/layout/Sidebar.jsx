import React from 'react';
import { useAuth } from '../../context/AuthContext';
import HeartbeatLogo from '../icons/HeartbeatLogo';

const iconProps = {
  width: 19,
  height: 19,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

const IconChart = () => (
  <svg {...iconProps}><path d="M4 19V9M11 19V5M18 19v-7" /></svg>
);

const IconUsers = () => (
  <svg {...iconProps}><path d="M16 19v-1.5a3.5 3.5 0 0 0-3.5-3.5h-5A3.5 3.5 0 0 0 4 17.5V19M10 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM20 19v-1.5a3 3 0 0 0-2.2-2.9M15 4.2a3 3 0 0 1 0 5.7" /></svg>
);

const IconFolder = () => (
  <svg {...iconProps}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /></svg>
);

const IconBrain = () => (
  <svg {...iconProps}>
    <path d="M8 4.5A2.5 2.5 0 0 0 5.5 7v.2A2.8 2.8 0 0 0 4 9.6v1A2.8 2.8 0 0 0 5.5 13v1.5A3.5 3.5 0 0 0 9 18a2 2 0 0 0 2-2V6.5A2 2 0 0 0 9 4.5H8Z" />
    <path d="M16 4.5A2.5 2.5 0 0 1 18.5 7v.2A2.8 2.8 0 0 1 20 9.6v1A2.8 2.8 0 0 1 18.5 13v1.5A3.5 3.5 0 0 1 15 18a2 2 0 0 1-2-2V6.5a2 2 0 0 1 2-2h1Z" />
  </svg>
);

const IconDocument = () => (
  <svg {...iconProps}><path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" /><path d="M13 3v5h5M9 13h6M9 17h6" /></svg>
);

const IconGear = () => (
  <svg {...iconProps}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 13a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V19a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H5a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H11a1.7 1.7 0 0 0 1-1.5V5a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V11a1.7 1.7 0 0 0 1.5 1H19a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" />
  </svg>
);

const ADMIN_MENU_ITEMS = [
  { id: 'admin-overview', Icon: IconChart, label: 'Tổng Quan Hệ Thống' },
  { id: 'admin-users', Icon: IconUsers, label: 'Quản Lý Tài Khoản' },
  { id: 'patient', Icon: IconFolder, label: 'Hồ Sơ Bệnh Nhân' },
  { id: 'settings', Icon: IconGear, label: 'Cài Đặt Hệ Thống' },
];

const CLINICAL_MENU_ITEMS = [
  { id: 'dashboard', Icon: IconChart, label: 'Theo Dõi Trực Tuyến' },
  { id: 'patient', Icon: IconFolder, label: 'Hồ Sơ Bệnh Nhân' },
  { id: 'xai', Icon: IconBrain, label: 'Phân Tích XAI Chuyên Sâu' },
  { id: 'reports', Icon: IconDocument, label: 'Xuất Báo Cáo (PDF/CSV)' },
];

const Sidebar = ({ activeTab, setActiveTab }) => {
  const { isAdmin } = useAuth();
  // "Cài Đặt Hệ Thống" (WS URL/ngưỡng cảnh báo) chỉ dành cho admin cấu hình - bác sĩ/y tá
  // không cần vào đây trong lúc trực, tránh vô tình đổi cấu hình đang ảnh hưởng tới màn theo dõi.
  const menuItems = isAdmin ? ADMIN_MENU_ITEMS : CLINICAL_MENU_ITEMS;

  return (
    <nav style={{
      width: '260px',
      minWidth: '260px',
      backgroundColor: 'var(--sidebar-bg)',
      display: 'flex',
      flexDirection: 'column',
      padding: '22px 0',
      zIndex: 10,
    }}>
      <div style={{ padding: '0 20px 20px', borderBottom: '1px solid rgba(255,255,255,0.08)', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '11px' }}>
          <div style={{
            width: '38px', height: '38px', borderRadius: '11px', flexShrink: 0,
            background: 'linear-gradient(135deg, var(--primary), #7c3aed)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 6px 16px rgba(47, 109, 246, 0.35)',
          }}>
            <span style={{ width: '20px', height: '20px', display: 'inline-flex' }}><HeartbeatLogo /></span>
          </div>
          <h2 style={{ margin: 0, color: '#ffffff', fontSize: '17px', fontWeight: '800', letterSpacing: '-0.03em' }}>
            NEURO-ECG
          </h2>
        </div>
        <p style={{ margin: '10px 0 0', fontSize: '11.5px', color: 'rgba(226,232,240,0.5)', letterSpacing: '0.02em' }}>
          Nền tảng giám sát tim mạch
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', padding: '0 14px' }}>
        {menuItems.map(({ id, Icon, label }) => {
          const isActive = activeTab === id;
          return (
            <div
              key={id}
              onClick={() => setActiveTab(id)}
              style={{
                padding: '11px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: 'pointer',
                borderRadius: '9px',
                backgroundColor: isActive ? 'var(--primary-bg)' : 'transparent',
                color: isActive ? 'var(--text-sidebar-active)' : 'var(--text-sidebar)',
                fontWeight: isActive ? '600' : '500',
                fontSize: '13.5px',
                transition: 'background-color 0.15s ease, color 0.15s ease',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <span style={{ display: 'inline-flex', flexShrink: 0 }}>
                <Icon />
              </span>
              {label}
            </div>
          );
        })}
      </div>
    </nav>
  );
};

export default Sidebar;
