import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { SunIcon, MoonIcon } from '../icons/ThemeIcons';

const Header = () => {
  const { isDarkActive, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header style={{
      height: '65px',
      minHeight: '65px',
      backgroundColor: 'var(--header-bg)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border-color)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 25px',
      zIndex: 5,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
        <h1 style={{ margin: 0, fontSize: '18px', color: 'var(--text-main)', fontWeight: '600' }}>Hệ Thống Theo Dõi Trung Tâm</h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <button
          type="button"
          onClick={toggleTheme}
          aria-label={isDarkActive ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
          title={isDarkActive ? 'Chế độ sáng' : 'Chế độ tối'}
          style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: '36px', height: '36px', borderRadius: '999px',
            border: '1px solid var(--border-color)', background: 'var(--theme-toggle-bg)',
            color: 'var(--theme-toggle-icon)', cursor: 'pointer',
          }}
        >
          <span style={{ width: '17px', height: '17px', display: 'inline-flex' }}>
            {isDarkActive ? <SunIcon /> : <MoonIcon />}
          </span>
        </button>

        <div ref={profileRef} style={{ position: 'relative' }}>
          <div 
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            style={{ 
              width: '38px', height: '38px', borderRadius: '50%', 
              backgroundColor: 'var(--primary-bg)', color: 'var(--primary)', 
              border: '1px solid var(--primary)', display: 'flex', 
              alignItems: 'center', justifyContent: 'center', 
              fontWeight: 'bold', fontSize: '14px', cursor: 'pointer',
              userSelect: 'none'
            }}
          >
            {user?.username ? user.username.substring(0, 2).toUpperCase() : 'NB'}
          </div>

          {isProfileOpen && (
            <div style={{
              position: 'absolute',
              top: '50px',
              right: '0',
              backgroundColor: 'var(--card-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '12px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              minWidth: '200px',
              zIndex: 10,
              display: 'flex',
              flexDirection: 'column',
              gap: '10px'
            }}>
              <div style={{ paddingBottom: '10px', borderBottom: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-main)' }}>{user?.username || 'Người dùng'}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{user?.role || 'Khách'}</div>
              </div>
              <button
                onClick={logout}
                style={{
                  padding: '8px', borderRadius: '4px', border: '1px solid var(--danger)',
                  background: 'transparent', color: 'var(--danger)',
                  cursor: 'pointer', fontWeight: '500', textAlign: 'center',
                  width: '100%', transition: 'all 0.2s'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = 'var(--danger)';
                  e.target.style.color = '#ffffff';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'transparent';
                  e.target.style.color = 'var(--danger)';
                }}
              >
                Đăng xuất
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
