import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { SunIcon, MoonIcon } from '../components/icons/ThemeIcons';
import HeartbeatLogo from '../components/icons/HeartbeatLogo';

// Vi tri co dinh (khong random) cho hat trang tri hero - tranh giat layout giua cac lan render/
// StrictMode double-invoke. Toa do % theo landing-shell.
const PARTICLES = [
  { top: '12%', left: '8%', delay: '0s', duration: '5.5s' },
  { top: '22%', left: '34%', delay: '1.2s', duration: '6.5s' },
  { top: '8%', left: '58%', delay: '2.1s', duration: '5s' },
  { top: '30%', left: '78%', delay: '0.6s', duration: '7s' },
  { top: '48%', left: '15%', delay: '1.8s', duration: '6s' },
  { top: '60%', left: '46%', delay: '0.3s', duration: '5.8s' },
  { top: '68%', left: '68%', delay: '2.6s', duration: '6.2s' },
  { top: '40%', left: '90%', delay: '1s', duration: '5.2s' },
  { top: '78%', left: '25%', delay: '1.5s', duration: '6.8s' },
  { top: '85%', left: '55%', delay: '0.9s', duration: '5.4s' },
];

// Nen "constellation" dong sau toan bo landing page: cac hat troi tu do va tu ket noi bang duong
// ke khi den gan nhau (ve bang canvas moi frame), lay cam hung tu nen dang o
// https://www.c3-app-165.io.vn/. Dung canvas (khong phai DOM node) vi so luong hat + duong noi
// thay doi lien tuc moi frame, dung DOM se rat nang. position:fixed nen luon phu kin man hinh
// va dung nguyen khi cuon trang (khong can ve lai theo chieu cao toan trang).
const NetworkBackground = ({ dark }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;
    const ctx = canvas.getContext('2d');
    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const NODE_COUNT = 52;
    const LINK_DIST = 140;
    const dotColor = dark ? 'rgba(147, 197, 253, 0.8)' : 'rgba(47, 109, 246, 0.55)';
    const lineColorBase = dark ? '150, 197, 253' : '47, 109, 246';

    let width = 0;
    let height = 0;
    let nodes = [];
    let rafId = null;

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const initNodes = () => {
      nodes = Array.from({ length: NODE_COUNT }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.4 + 1.1,
      }));
    };

    const drawFrame = () => {
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < nodes.length; i += 1) {
        for (let j = i + 1; j < nodes.length; j += 1) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < LINK_DIST) {
            ctx.strokeStyle = `rgba(${lineColorBase}, ${(1 - dist / LINK_DIST) * 0.32})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        }
      }

      ctx.fillStyle = dotColor;
      for (const n of nodes) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    const step = () => {
      for (const n of nodes) {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x <= 0 || n.x >= width) n.vx *= -1;
        if (n.y <= 0 || n.y >= height) n.vy *= -1;
      }
      drawFrame();
      rafId = requestAnimationFrame(step);
    };

    resize();
    initNodes();

    if (reduceMotion) {
      drawFrame();
    } else {
      step();
    }

    const handleResize = () => {
      resize();
      initNodes();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      window.removeEventListener('resize', handleResize);
    };
  }, [dark]);

  return <canvas ref={canvasRef} className="network-canvas" aria-hidden="true" />;
};

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
  const { login } = useAuth();
  const [view, setView] = useState('landing');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { isDarkActive, toggleTheme } = useTheme();

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

  const openLogin = () => {
    resetForm();
    setView('login');
  };

  const renderAuthCard = () => (
    <div className="identity-card">
      <div className="card-header">
        <div>
          <p>Hệ thống chăm sóc tim mạch</p>
          <h3>Đăng nhập</h3>
        </div>
        <button type="button" className="mini-link" onClick={() => setView('landing')}>
          Quay lại
        </button>
      </div>

      <form className="auth-form" onSubmit={handleLogin}>
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
          {loading ? 'Đang đăng nhập...' : 'Đăng nhập hệ thống'}
        </button>
      </form>
    </div>
  );

  return (
    <div className="landing-shell">
      <NetworkBackground dark={isDarkActive} />
      <div className="landing-glow glow-one" />
      <div className="landing-glow glow-two" />

      <header className="landing-header">
        <div className="brand-wrap" aria-label="NEURO-ECG brand">
          <div className="brand-mark"><HeartbeatLogo /></div>
          <div className="brand-text">
            <span>NEURO</span>-ECG
          </div>
        </div>

        <nav className="landing-nav" aria-label="Main navigation">
          <a href="#features">Tính năng</a>
          <a href="#workflow">Quy trình</a>
          <a href="#metrics">Hiệu suất</a>
        </nav>

        <div className="header-actions">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={isDarkActive ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
            title={isDarkActive ? 'Chế độ sáng' : 'Chế độ tối'}
          >
            {isDarkActive ? <SunIcon /> : <MoonIcon />}
          </button>
          <button type="button" className="nav-button" onClick={openLogin}>
            Đăng nhập
          </button>
        </div>
      </header>

      <main className="landing-main">
        {view === 'landing' ? (
          <section className="hero-section">
            <div className="particle-field" aria-hidden="true">
              {PARTICLES.map((p, i) => (
                <span key={i} style={{ top: p.top, left: p.left, animationDelay: p.delay, animationDuration: p.duration }} />
              ))}
            </div>

            <div className="hero-copy fade-in-up" style={{ animationDelay: '0.05s' }}>
              <div className="eyebrow">
                <span className="eyebrow-dot" />
                GIÁM SÁT NHỊP TIM AI · THỜI GIAN THỰC
              </div>
              <h1>
                Giám sát ECG theo thời gian thực
                <span> và cảnh báo sớm bất thường</span>
              </h1>
              <p>
                Nền tảng AI giúp bệnh viện theo dõi nhịp tim, nhận diện bất thường, và hỗ trợ bác sĩ ra quyết định nhanh
                hơn bằng dữ liệu ECG trực quan và báo cáo kịp thời.
              </p>

              <div className="cta-row">
                <button type="button" className="primary-button" onClick={openLogin}>Bắt đầu ngay</button>
              </div>
            </div>

            <div className="hero-visual fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="pulse-panel large-pulse">
                <div className="pulse-header">
                  <span className="pulse-title">Tín hiệu ECG trực tiếp</span>
                  <span className="live-badge">
                    <span className="live-dot" />
                    TRỰC TIẾP
                  </span>
                </div>
                <div className="pulse-line" style={{ background: 'transparent', boxShadow: 'none', height: '80px', overflow: 'hidden' }}>
                  <svg viewBox="0 0 1000 100" preserveAspectRatio="none" className="ecg-line-svg" style={{ width: '200%', height: '100%', stroke: 'var(--primary)', filter: 'drop-shadow(0 2px 4px rgba(47,109,246,0.3))', animation: 'ecg-scroll 4s linear infinite' }}>
                    <polyline points="0,50 50,50 60,40 70,50 90,50 100,20 110,90 120,50 150,50 160,45 170,50 220,50 230,40 240,50 260,50 270,20 280,90 290,50 320,50 330,45 340,50 390,50 400,40 410,50 430,50 440,20 450,90 460,50 500,50 550,50 560,40 570,50 590,50 600,20 610,90 620,50 650,50 660,45 670,50 720,50 730,40 740,50 760,50 770,20 780,90 790,50 820,50 830,45 840,50 890,50 900,40 910,50 930,50 940,20 950,90 960,50 1000,50" fill="none" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div className="pulse-stats">
                  <div className="pulse-stat">
                    <span className="pulse-stat-label">Nhịp tim</span>
                    <span className="pulse-stat-value">72 <span className="pulse-stat-unit">bpm</span></span>
                  </div>
                  <div className="pulse-stat pulse-stat-end">
                    <span className="pulse-stat-label">Nhịp điệu</span>
                    <span className="pulse-stat-value" style={{ color: 'var(--success)' }}>Bình thường</span>
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
              <h2>Đăng nhập để tiếp tục</h2>
              <p>Quản lý bệnh nhân, theo dõi ECG và xử lý cảnh báo trong một giao diện thống nhất.</p>
              <p className="auth-note">
                Chưa có tài khoản? Liên hệ quản trị viên bệnh viện để được cấp tài khoản —
                hệ thống không hỗ trợ tự đăng ký.
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
              {features.map((feature, index) => (
                <article key={feature.title} className="feature-card fade-in-up" style={{ animationDelay: `${index * 0.12}s` }}>
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
                  <div key={step} className="workflow-card fade-in-up" style={{ animationDelay: `${index * 0.12}s` }}>
                    <div className="step-number">0{index + 1}</div>
                    <h3>{step}</h3>
                  </div>
                ))}
              </div>
            </section>

            <section className="workflow-section" id="metrics" style={{ marginTop: '64px' }}>
              <div className="section-heading">
                <span>HIỆU SUẤT ĐÃ KIỂM CHỨNG</span>
                <h2>Số liệu thực đo, sẵn sàng cho triển khai bệnh viện</h2>
              </div>

              <div className="workflow-grid">
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0s' }}>
                  <div className="step-number" style={{ background: 'rgba(23, 178, 106, 0.12)', color: 'var(--success)', width: 'auto', padding: '0 16px' }}>98.4%</div>
                  <h3>Độ chính xác trên tập kiểm thử</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Đo trên 21.892 nhịp tim độc lập (chuẩn MIT-BIH), sau khi đối sánh 5 kiến trúc AI khác nhau để chọn mô hình triển khai tối ưu.</p>
                </div>
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0.12s' }}>
                  <div className="step-number" style={{ background: 'var(--primary-soft)', color: 'var(--primary-strong)', width: 'auto', padding: '0 16px' }}>~3 ms</div>
                  <h3>Độ trễ xử lý trung bình</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Từ lúc phát hiện nhịp bất thường đến khi đóng gói cảnh báo gửi đi, đo thực tế trên 600 nhịp tim liên tiếp.</p>
                </div>
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0.24s' }}>
                  <div className="step-number" style={{ background: 'rgba(245, 158, 11, 0.12)', color: 'var(--warning)', width: 'auto', padding: '0 16px' }}>10 giường</div>
                  <h3>Giám sát đồng thời ổn định / node</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Trên 1 máy chủ backend; dễ mở rộng thêm bằng cân bằng tải khi triển khai ở quy mô khoa/bệnh viện lớn hơn.</p>
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
