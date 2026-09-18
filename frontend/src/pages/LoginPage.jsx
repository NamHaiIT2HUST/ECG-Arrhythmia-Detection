import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';

const THEME_KEY = 'ecg_theme';

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

const HeartbeatLogo = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M3 12h3.5l1.5-4 3 8 2-5.5 1.5 3.5H21"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const SunIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="4.5" stroke="currentColor" strokeWidth="2" />
    <path d="M12 2.5v2.5M12 19v2.5M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2.5 12H5M19 12h2.5M4.2 19.8 6 18M18 6l1.8-1.8"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
);

const MoonIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
  </svg>
);

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
  const { login, register } = useAuth();
  const [view, setView] = useState('landing');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Theme: 'light' | 'dark' | null (null = theo he thong, khong ep). Ap dung bang attribute
  // data-theme tren <html> - CSS (index.css) doc attribute nay de ghi de bang mau. Landing
  // page truoc day CHI theo prefers-color-scheme cua he dieu hanh, khong co nut bam thu cong.
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) || null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme) {
      root.setAttribute('data-theme', theme);
    } else {
      root.removeAttribute('data-theme');
    }
    try {
      if (theme) localStorage.setItem(THEME_KEY, theme);
      else localStorage.removeItem(THEME_KEY);
    } catch {
      // localStorage khong kha dung (private mode...) - bo qua, theme van hoat dong trong phien
    }
  }, [theme]);

  const isDarkActive = theme
    ? theme === 'dark'
    : typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  const toggleTheme = () => setTheme(isDarkActive ? 'light' : 'dark');

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
                <button type="button" className="primary-button" onClick={openRegister}>Bắt đầu miễn phí</button>
              </div>
            </div>

            <div className="hero-visual fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="pulse-panel large-pulse">
                <div className="pulse-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)' }}>Real-time ECG Stream</span>
                </div>
                <div className="pulse-line" style={{ background: 'transparent', boxShadow: 'none', height: '80px', overflow: 'hidden' }}>
                  <svg viewBox="0 0 1000 100" preserveAspectRatio="none" className="ecg-line-svg" style={{ width: '200%', height: '100%', stroke: 'var(--primary)', filter: 'drop-shadow(0 2px 4px rgba(47,109,246,0.3))', animation: 'ecg-scroll 4s linear infinite' }}>
                    <polyline points="0,50 50,50 60,40 70,50 90,50 100,20 110,90 120,50 150,50 160,45 170,50 220,50 230,40 240,50 260,50 270,20 280,90 290,50 320,50 330,45 340,50 390,50 400,40 410,50 430,50 440,20 450,90 460,50 500,50 550,50 560,40 570,50 590,50 600,20 610,90 620,50 650,50 660,45 670,50 720,50 730,40 740,50 760,50 770,20 780,90 790,50 820,50 830,45 840,50 890,50 900,40 910,50 930,50 940,20 950,90 960,50 1000,50" fill="none" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
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
                      <span style={{ width: '6px', height: '6px', background: 'var(--danger)', borderRadius: '50%', display: 'inline-block', animation: 'pulse-dot 1.5s ease-in-out infinite' }}></span> LIVE
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
                <span>HIỆU SUẤT</span>
                <h2>Độ tin cậy và hiệu suất vượt trội</h2>
              </div>

              <div className="workflow-grid">
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0s' }}>
                  <div className="step-number" style={{ background: 'var(--primary-soft)', color: 'var(--primary-strong)' }}>24/7</div>
                  <h3>Giám sát liên tục</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Hệ thống hoạt động không gián đoạn, luôn sẵn sàng phân tích tín hiệu 24 giờ mỗi ngày.</p>
                </div>
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0.12s' }}>
                  <div className="step-number" style={{ background: 'rgba(23, 178, 106, 0.12)', color: 'var(--success)', width: 'auto', padding: '0 16px' }}>99.2%</div>
                  <h3>Độ chính xác cao</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Mô hình AI được huấn luyện chuyên sâu với độ chính xác và tin cậy đạt chuẩn y tế.</p>
                </div>
                <div className="workflow-card fade-in-up" style={{ animationDelay: '0.24s' }}>
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
