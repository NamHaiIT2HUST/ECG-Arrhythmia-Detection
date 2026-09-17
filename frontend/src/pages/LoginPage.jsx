import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const features = [
  { title: 'AI cảnh báo sớm', text: 'Phân tích nhịp tim theo thời gian thực và phát hiện bất thường sớm.' },
  { title: 'Báo cáo bệnh nhân', text: 'Tự động tổng hợp ECG, nhịp tim và dòng sự kiện quan trọng.' },
  { title: 'Phân quyền rõ ràng', text: 'Admin, bác sĩ và y tá có vai trò phù hợp với từng giao diện.' },
];

const steps = [
  'Thu thập tín hiệu ECG từ thiết bị',
  'Phân tích nhịp và phát hiện bất thường',
  'Hiển thị cảnh báo và báo cáo cho nhân sự y tế',
];


const LoginPage = () => {
  const { login, register } = useAuth();
  const [view, setView] = useState('landing');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const resetForm = () => {
    setUsername('');
    setPassword('');
    setError(null);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng nhập thất bại. Kiểm tra lại tên tài khoản và mật khẩu.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({ username, password });
      await login(username, password);
    } catch (err) {
      setError(err.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const openLogin = () => {
    resetForm();
    setView('login');
  };

  const openRegister = () => {
    resetForm();
    setView('register');
  };

  const renderAuthCard = () => {
    const isLogin = view === 'login';
    const isRegister = view === 'register';

    return (
      <div className="identity-card">
        <div className="card-header">
          <div>
            <p>Hệ thống chăm sóc tim mạch</p>
            <h3>{isLogin ? 'Đăng nhập' : 'Đăng ký tài khoản'}</h3>
          </div>
          <button type="button" className="mini-link" onClick={() => setView('landing')}>
            Quay lại
          </button>
        </div>

        <form className="auth-form" onSubmit={isLogin ? handleLogin : handleRegister}>
          {/* Role selection removed: public registrations are always created as nurse on the server. */}

          <label>
            <span>Tên đăng nhập</span>
            <input
              type="text"
              placeholder="Nhập tên tài khoản"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
            />
          </label>

          <label>
            <span>Mật khẩu</span>
            <input
              type="password"
              placeholder="Nhập mật khẩu"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && <div className="error-box">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading || !username || !password}>
            {loading ? (isLogin ? 'Đang đăng nhập...' : 'Đang đăng ký...') : (isLogin ? 'Đăng nhập hệ thống' : 'Tạo tài khoản')}
          </button>

          {isLogin && (
            <button type="button" className="secondary-button compact-button" onClick={openRegister}>
              Tạo tài khoản mới
            </button>
          )}
        </form>
      </div>
    );
  };

  return (
    <div className="landing-shell">
      <div className="landing-glow glow-one" />
      <div className="landing-glow glow-two" />

      <header className="landing-header">
        <div className="brand-wrap" aria-label="CardioVision brand">
          <div className="brand-mark">ECG</div>
          <div className="brand-text" style={{ color: 'var(--text-main)' }}>
            <span style={{ color: 'var(--text-main)' }}>NEURO</span>-ECG
          </div>
        </div>

        <nav className="landing-nav" aria-label="Main navigation">
          <a href="#features">Tính năng</a>
          <a href="#workflow">Quy trình</a>
          <a href="#metrics">Hiệu suất</a>
        </nav>

        <button type="button" className="nav-button" onClick={openLogin}>
          Đăng nhập
        </button>
      </header>

      <main className="landing-main">
        {view === 'landing' ? (
          <section className="hero-section">
            <div className="hero-copy">
              <div className="eyebrow">PHÒNG NGỪA TỔN THƯƠNG TIM MẠNH</div>
              <h1>
                Giám sát ECG theo thời gian thực
                <span> và cảnh báo sớm bất thường</span>
              </h1>
              <p>
                Nền tảng AI giúp bệnh viện theo dõi nhịp tim, nhận diện bất thường, và hỗ trợ bác sĩ ra quyết định nhanh
                hơn bằng dữ liệu ECG trực quan và báo cáo kịp thời.
              </p>

              <div className="cta-row">
                <button type="button" className="primary-button" onClick={openRegister}>Bắt đầu miễn phí</button>
              </div>
            </div>

            <div className="hero-visual">
              <div className="pulse-panel large-pulse">
                <div className="pulse-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)' }}>Real-time ECG Stream</span>
                </div>
                <div className="pulse-line" style={{ background: 'transparent', boxShadow: 'none', height: '80px' }}>
                  <svg viewBox="0 0 500 100" className="ecg-line-svg" style={{ width: '100%', height: '100%', stroke: 'var(--primary)', filter: 'drop-shadow(0 2px 4px rgba(47,109,246,0.3))' }}>
                    <polyline points="0,50 50,50 60,40 70,50 90,50 100,20 110,90 120,50 150,50 160,45 170,50 220,50 230,40 240,50 260,50 270,20 280,90 290,50 320,50 330,45 340,50 390,50 400,40 410,50 430,50 440,20 450,90 460,50 500,50" fill="none" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div className="pulse-stats" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Heart Rate</span>
                    <span style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)' }}>72 <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)' }}>bpm</span></span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Rhythm Status</span>
                    <span style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--success)' }}>Normal Sinus</span>
                    <span className="live-badge" style={{ fontSize: '0.65rem', padding: '2px 8px', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 'bold', marginTop: '6px' }}>
                      <span style={{ width: '6px', height: '6px', background: 'var(--danger)', borderRadius: '50%', display: 'inline-block', animation: 'pulse 1.5s infinite' }}></span> LIVE
                    </span>
                  </div>
                </div>
              </div>
              <div className="mini-stat stat-two">
                <span>Cảnh báo bất thường</span>
                <strong>12 ca / ngày</strong>
              </div>
            </div>
          </section>
        ) : (
          <section className="auth-layout">
            <div className="auth-copy">
              <div className="eyebrow">TRUNG TÂM CHĂM SÓC TIM MẠCH</div>
              <h2>{view === 'login' ? 'Đăng nhập để tiếp tục' : 'Tạo tài khoản mới'}</h2>
              <p>
                {view === 'login'
                  ? 'Quản lý bệnh nhân, theo dõi ECG và xử lý cảnh báo trong một giao diện thống nhất.'
                  : 'Chọn vai trò, tạo tên đăng nhập và mật khẩu để bắt đầu sử dụng hệ thống.'}
              </p>
            </div>
            {renderAuthCard()}
          </section>
        )}

        {view === 'landing' && (
          <>
            <section className="feature-section" id="features">
              <div className="section-heading" style={{ gridColumn: '1 / -1' }}>
                <span>TÍNH NĂNG</span>
                <h2>Các tính năng nổi bật của hệ thống</h2>
              </div>
              {features.map((feature) => (
                <article key={feature.title} className="feature-card">
                  <div className="feature-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/>
                      <path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/>
                      <circle cx="20" cy="10" r="2"/>
                    </svg>
                  </div>
                  <h3>{feature.title}</h3>
                  <p>{feature.text}</p>
                </article>
              ))}
            </section>

            <section className="workflow-section" id="workflow">
              <div className="section-heading">
                <span>QUY TRÌNH HOẠT ĐỘNG</span>
                <h2>Ba bước từ tín hiệu ECG đến cảnh báo y tế</h2>
              </div>

              <div className="workflow-grid">
                {steps.map((step, index) => (
                  <div key={step} className="workflow-card">
                    <div className="step-number">0{index + 1}</div>
                    <h3>{step}</h3>
                  </div>
                ))}
              </div>
            </section>

            <section className="workflow-section" id="metrics" style={{ marginTop: '64px' }}>
              <div className="section-heading">
                <span>HIỆU SUẤT</span>
                <h2>Độ tin cậy và hiệu suất vượt trội</h2>
              </div>

              <div className="workflow-grid">
                <div className="workflow-card">
                  <div className="step-number" style={{ background: 'var(--primary-soft)', color: 'var(--primary-strong)' }}>24/7</div>
                  <h3>Giám sát liên tục</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Hệ thống hoạt động không gián đoạn, luôn sẵn sàng phân tích tín hiệu 24 giờ mỗi ngày.</p>
                </div>
                <div className="workflow-card">
                  <div className="step-number" style={{ background: 'rgba(23, 178, 106, 0.12)', color: 'var(--success)', width: 'auto', padding: '0 16px' }}>99.2%</div>
                  <h3>Độ chính xác cao</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Mô hình AI được huấn luyện chuyên sâu với độ chính xác và tin cậy đạt chuẩn y tế.</p>
                </div>
                <div className="workflow-card">
                  <div className="step-number" style={{ background: 'rgba(245, 158, 11, 0.12)', color: 'var(--warning)' }}>03</div>
                  <h3>Vai trò linh hoạt</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Phân quyền rõ ràng cho Admin, Bác sĩ và Y tá, phù hợp với luồng công việc bệnh viện.</p>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
};

export default LoginPage;
