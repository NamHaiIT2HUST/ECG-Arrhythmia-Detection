import React, { useState, Suspense } from 'react';
import DashboardPage from './pages/DashboardPage';
import XAIPage from './pages/XAIPage';
import ReportExporter from './pages/ReportExporter';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import { AnomalyProvider } from './context/AnomalyContext';
import { PatientProvider } from './context/PatientContext';
import { AlarmProvider } from './context/AlarmContext';
import PatientPage from './pages/PatientPage';
import SettingsPage from './pages/SettingsPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';

const PatientList = React.lazy(() => import('./components/patients/PatientList'));

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  return (
    <AuthProvider>
      <AnomalyProvider>
        <PatientProvider>
          <AlarmProvider>
            <InnerApp activeTab={activeTab} setActiveTab={setActiveTab} />
          </AlarmProvider>
        </PatientProvider>
      </AnomalyProvider>
    </AuthProvider>
  );
}

const InnerApp = ({ activeTab, setActiveTab }) => {
  const { isAuthenticated, isAdmin, authLoading } = useAuth();

  if (authLoading) {
    return (
      <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        Đang xác thực phiên đăng nhập...
      </div>
    );
  }
  if (!isAuthenticated) return <LoginPage />;

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-color)' }}>
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          {activeTab === 'dashboard' && <DashboardPage />}
          {activeTab === 'patient' && (
            <div style={{ padding: '25px' }}>
              <div className="card" style={{ padding: '20px' }}>
                <h2 style={{ color: 'var(--text-main)' }}>Hồ Sơ Bệnh Nhân</h2>
                <p style={{ color: 'var(--text-muted)' }}>Quản lý bệnh nhân (localStorage) — thêm/sửa/chọn để gán phiên stream.</p>
                <div style={{ marginTop: 12 }}>
                  <div style={{ display: 'flex', gap: 12 }}>
                    <div style={{ flex: 1 }}>
                        {/* PatientList component lazy-loaded to avoid bumping initial bundle */}
                        <Suspense fallback={<div>Đang tải...</div>}>
                          <PatientList />
                        </Suspense>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'xai' && <XAIPage />}
          {activeTab === 'reports' && <ReportExporter />}
          {activeTab === 'settings' && isAdmin && <SettingsPage />}
        </main>
      </div>
    </div>
  );
};

export default App;