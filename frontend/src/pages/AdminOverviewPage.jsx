import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { usePatient } from '../context/PatientContext';

const ROLE_LABEL = { admin: 'Quản trị viên', doctor: 'Bác sĩ', nurse: 'Y tá' };

const StatCard = ({ label, value, unit, accent, note }) => (
  <div style={{
    backgroundColor: 'var(--card-bg)',
    border: '1px solid var(--border-color)',
    borderRadius: '10px',
    padding: '20px 22px',
    borderLeft: `4px solid ${accent}`,
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  }}>
    <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
      {label}
    </span>
    <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
      <span style={{ fontSize: '28px', fontWeight: '700', color: 'var(--text-main)' }}>{value}</span>
      {unit && <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{unit}</span>}
    </div>
    {note && <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>{note}</p>}
  </div>
);

const AdminOverviewPage = () => {
  const { patients } = usePatient();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await api.get('/api/admin/stats');
        if (!cancelled) setStats(res.data);
      } catch (err) {
        if (!cancelled) setError(err.response?.data?.detail || 'Không tải được số liệu thống kê.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const totalUsers = stats ? Object.values(stats.users_by_role).reduce((a, b) => a + b, 0) : null;

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ margin: '0 0 4px', color: 'var(--text-main)', fontSize: '22px', fontWeight: '700' }}>
          Tổng Quan Hệ Thống
        </h2>
        <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)' }}>
          Số liệu tài khoản, bệnh nhân và hoạt động giám sát trên toàn hệ thống.
        </p>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', borderRadius: '8px', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.25)', color: 'var(--danger)', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {loading ? (
        <p style={{ color: 'var(--text-muted)' }}>Đang tải...</p>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            <StatCard
              label="Tổng số tài khoản"
              value={totalUsers ?? '--'}
              unit="tài khoản"
              accent="var(--primary)"
            />
            <StatCard
              label="Bệnh nhân đang quản lý"
              value={patients.length}
              unit="bệnh nhân"
              accent="#10b981"
              note="Theo dữ liệu hồ sơ bệnh nhân đang lưu trên trình duyệt này."
            />
            <StatCard
              label="Cảnh báo bất thường đã ghi nhận"
              value={stats?.total_anomalies ?? '--'}
              unit="sự kiện"
              accent="#f59e0b"
            />
          </div>

          <div style={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '20px 22px' }}>
            <h3 style={{ margin: '0 0 14px', fontSize: '15px', color: 'var(--text-main)', fontWeight: '600' }}>
              Phân bổ tài khoản theo vai trò
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats && Object.entries(stats.users_by_role).map(([role, count]) => (
                <div key={role} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border-color)' }}>
                  <span style={{ fontSize: '14px', color: 'var(--text-main)' }}>{ROLE_LABEL[role] || role}</span>
                  <span style={{ fontSize: '14px', fontWeight: '700', color: 'var(--primary)' }}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminOverviewPage;
