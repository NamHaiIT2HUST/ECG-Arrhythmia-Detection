import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('nurse');

  const handleSubmit = (e) => {
    e.preventDefault();
    const u = login(username || undefined, role);
    console.debug('[LoginPage] logged in', u);
    // Force reload so the top-level guard sees the persisted user immediately
    try {
      window.location.reload();
    } catch (e) {
      /* noop */
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-color)' }}>
      <div className="card" style={{ padding: 24, width: 420 }}>
        <h2 style={{ marginTop: 0 }}>Đăng nhập (mock)</h2>
        <p style={{ color: 'var(--text-muted)' }}>Chọn tên và vai trò để mô phỏng phân quyền frontend.</p>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input placeholder="Tên người dùng" value={username} onChange={e => setUsername(e.target.value)} style={{ padding: 10, borderRadius: 6, border: '1px solid var(--border-color)' }} />
          <select value={role} onChange={e => setRole(e.target.value)} style={{ padding: 10, borderRadius: 6, border: '1px solid var(--border-color)' }}>
            <option value="admin">Admin</option>
            <option value="doctor">Doctor</option>
            <option value="nurse">Nurse</option>
          </select>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button type="submit" style={{ padding: '8px 12px', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: 6 }}>Đăng nhập</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
