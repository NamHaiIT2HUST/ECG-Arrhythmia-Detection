import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      // Không cần reload thủ công - login() cập nhật state của AuthContext, App.jsx tự
      // render lại sang giao diện chính ngay khi isAuthenticated đổi thành true.
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại. Kiểm tra lại kết nối tới backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-color)' }}>
      <div className="card" style={{ padding: 24, width: 380 }}>
        <h2 style={{ marginTop: 0, color: 'var(--text-main)' }}>🫀 Đăng nhập</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Đăng nhập bằng tài khoản đã được cấp để vào hệ thống giám sát ECG.</p>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <input
            placeholder="Tên đăng nhập"
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoFocus
            style={{ padding: 10, borderRadius: 6, border: '1px solid var(--border-color)' }}
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={{ padding: 10, borderRadius: 6, border: '1px solid var(--border-color)' }}
          />
          {error && <div style={{ color: 'var(--danger)', fontSize: 13 }}>{error}</div>}
          <button
            type="submit"
            disabled={loading || !username || !password}
            style={{
              padding: '10px 12px',
              background: loading || !username || !password ? '#94a3b8' : 'var(--primary)',
              color: 'white',
              border: 'none',
              borderRadius: 6,
              cursor: loading || !username || !password ? 'not-allowed' : 'pointer',
              fontWeight: 600,
            }}
          >
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;
