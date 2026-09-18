import React, { useEffect, useState } from 'react';
import api from '../api/axios';

const ROLE_LABEL = { admin: 'Quản trị viên', doctor: 'Bác sĩ', nurse: 'Y tá' };
const ROLE_OPTIONS = ['nurse', 'doctor', 'admin'];

const sectionStyle = {
  backgroundColor: 'var(--card-bg)',
  border: '1px solid var(--border-color)',
  borderRadius: '10px',
  padding: '22px',
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

const formatDate = (iso) => {
  try {
    return new Date(iso).toLocaleString('vi-VN');
  } catch {
    return iso;
  }
};

const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [listError, setListError] = useState(null);

  const [form, setForm] = useState({ username: '', password: '', role: 'nurse' });
  const [formError, setFormError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/admin/users');
      setUsers(res.data);
      setListError(null);
    } catch (err) {
      setListError(err.response?.data?.detail || 'Không tải được danh sách tài khoản.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const updateForm = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      await api.post('/api/admin/users', form);
      setForm({ username: '', password: '', role: 'nurse' });
      await loadUsers();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Tạo tài khoản thất bại. Vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '1100px' }}>
      <div>
        <h2 style={{ margin: '0 0 4px', color: 'var(--text-main)', fontSize: '22px', fontWeight: '700' }}>
          Quản Lý Tài Khoản
        </h2>
        <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)' }}>
          Chỉ admin được tạo tài khoản mới cho bác sĩ/y tá — hệ thống không hỗ trợ tự đăng ký.
        </p>
      </div>

      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 14px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          Thêm tài khoản mới
        </h3>
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 180px' }}>
            <label style={{ fontSize: '13px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Tên đăng nhập</label>
            <input
              style={inputStyle}
              value={form.username}
              onChange={(e) => updateForm('username', e.target.value)}
              placeholder="vd: bs_nguyen"
              required
            />
          </div>
          <div style={{ flex: '1 1 180px' }}>
            <label style={{ fontSize: '13px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Mật khẩu</label>
            <input
              type="password"
              style={inputStyle}
              value={form.password}
              onChange={(e) => updateForm('password', e.target.value)}
              placeholder="Ít nhất 6 ký tự"
              required
            />
          </div>
          <div style={{ flex: '0 0 160px' }}>
            <label style={{ fontSize: '13px', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>Vai trò</label>
            <select
              style={inputStyle}
              value={form.role}
              onChange={(e) => updateForm('role', e.target.value)}
            >
              {ROLE_OPTIONS.map((role) => (
                <option key={role} value={role}>{ROLE_LABEL[role]}</option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={submitting || !form.username || !form.password}
            style={{
              padding: '10px 20px', backgroundColor: 'var(--primary)', color: 'white',
              border: 'none', borderRadius: '6px', fontWeight: '600', cursor: 'pointer',
              opacity: submitting ? 0.7 : 1,
            }}
          >
            {submitting ? 'Đang tạo...' : 'Tạo tài khoản'}
          </button>
        </form>
        {formError && (
          <div style={{ marginTop: '12px', padding: '10px 14px', borderRadius: '6px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', color: 'var(--danger)', fontSize: '13px' }}>
            {formError}
          </div>
        )}
      </div>

      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 14px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
          Danh sách tài khoản ({users.length})
        </h3>
        {listError && (
          <div style={{ padding: '10px 14px', borderRadius: '6px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', color: 'var(--danger)', fontSize: '13px', marginBottom: '12px' }}>
            {listError}
          </div>
        )}
        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Đang tải...</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '10px 8px', color: 'var(--text-muted)', fontWeight: '600' }}>Tên đăng nhập</th>
                  <th style={{ padding: '10px 8px', color: 'var(--text-muted)', fontWeight: '600' }}>Vai trò</th>
                  <th style={{ padding: '10px 8px', color: 'var(--text-muted)', fontWeight: '600' }}>Ngày tạo</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '10px 8px', color: 'var(--text-main)', fontWeight: '600' }}>{u.username}</td>
                    <td style={{ padding: '10px 8px', color: 'var(--text-main)' }}>{ROLE_LABEL[u.role] || u.role}</td>
                    <td style={{ padding: '10px 8px', color: 'var(--text-muted)' }}>{formatDate(u.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUsersPage;
