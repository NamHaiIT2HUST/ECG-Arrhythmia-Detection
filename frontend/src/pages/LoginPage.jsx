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

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'doctor', label: 'Bác sĩ' },
  { value: 'nurse', label: 'Y tá' },
];

const LoginPage = () => {
  const { login, register } = useAuth();
  const [view, setView] = useState('landing');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('doctor');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const resetForm = () => {
    setUsername('');
    setPassword('');
    setRole('doctor');
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
      await register({ username, password, role });
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
          {isRegister && (
            <label>
              <span>Vai trò</span>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                {roleOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          )}

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
          <div className="brand-text" style={{ color: '#000000' }}>
            <span style={{ color: '#000000' }}>NEURO</span>-ECG
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

              <div className="trust-row" id="metrics">
                <div>
                  <strong>24/7</strong>
                  <span>Giám sát liên tục</span>
                </div>
                <div>
                  <strong>99.2%</strong>
                  <span>Độ chính xác mô hình</span>
                </div>
                <div>
                  <strong>3</strong>
                  <span>Vai trò người dùng</span>
                </div>
              </div>
            </div>

            <div className="hero-visual">
              <div className="pulse-panel large-pulse">
                <div className="pulse-line" />
                <div className="pulse-stats">
                  <span>HR: 72 bpm</span>
                  <span>Rhythm: Normal</span>
                </div>
              </div>
              <div className="mini-stat stat-one">
                <span>Chẩn đoán</span>
                <strong>96.8%</strong>
              </div>
              <div className="mini-stat stat-two">
                <span>Cảnh báo</span>
                <strong>12 vụ</strong>
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
              {features.map((feature) => (
                <article key={feature.title} className="feature-card">
                  <div className="feature-icon">✦</div>
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
          </>
        )}
      </main>
    </div>
  );
};

export default LoginPage;
