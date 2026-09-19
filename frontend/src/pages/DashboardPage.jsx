import React, { useState, useEffect } from 'react';
import StatCards from '../components/dashboard/StatCards';
import ECGChart from '../components/dashboard/ECGChart';
import LoadingSpinner from '../components/dashboard/LoadingSpinner';
import UploadDiagnosisModal from '../components/dashboard/UploadDiagnosisModal';
import ReportButton from '../components/ReportButton';
import { usePatient } from '../context/PatientContext';
import { useMonitoring } from '../context/MonitoringContext';
import { useAlarm } from '../context/AlarmContext';

const DashboardPage = () => {
  const {
    connectionStatus,
    isInitialLoading,
    xData,
    yData,
    yData2,
    lead1Name,
    lead2Name,
    currentHeatmap,
    latestPrediction,
    latencyE2e,
    bpm,
    hrvSdnn,
    hrvRmssd,
    confidence,
    afibSuspected,
    afibScore,
    tachycardiaSuspected,
    sessionStartedAt,
    totalBeats,
    confidenceThreshold,
  } = useMonitoring();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedError, setSeedError] = useState(null);

  const { patients, selectedPatient, setSelectedPatient, seedDemoPatients } = usePatient();
  const { currentAlarmLevel, currentAlarmLabel } = useAlarm();

  // Ref cho báo cáo PDF - trỏ tới DOM đang render hiện tại nên phải ở lại component (không
  // chuyển vào MonitoringContext cùng phần dữ liệu stream).
  const chartRef = React.useRef(null);

  const handleSeedDemoPatients = async () => {
    setIsSeeding(true);
    setSeedError(null);
    try {
      const count = await seedDemoPatients();
      if (count === 0) setSeedError('Tất cả bản ghi mẫu đã có bệnh nhân tương ứng.');
    } catch {
      setSeedError('Không tạo được bệnh nhân mẫu. Kiểm tra kết nối backend.');
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>

      {/* Thanh trạng thái hợp nhất: gộp định danh bệnh nhân + cụm trạng thái/hành động vào
          CÙNG 1 khối duy nhất thay vì nhiều chip/nút rời rạc tự phong cách riêng (badge tròn,
          nút xanh lá, nút xanh dương... không cùng 1 hệ thống) như trước - giữ nguyên toàn bộ
          thông tin, chỉ tổ chức lại theo đúng phân cấp: cảnh báo mới cần màu mạnh/nổi bật,
          còn lại (xuất báo cáo, chẩn đoán offline) là hành động phụ nên dùng nút viền đồng bộ. */}
      <div className="card" style={{ padding: '14px 22px', display: 'flex', flexDirection: 'column', gap: selectedPatient ? '10px' : 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          {selectedPatient ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '10px', flexShrink: 0,
                backgroundColor: 'var(--primary-bg)', color: 'var(--primary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '19px',
              }}>🧑‍⚕️</div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '15px', fontWeight: '700', color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {selectedPatient.name}
                  <span style={{ fontWeight: '500', color: 'var(--text-muted)', fontSize: '13px' }}>
                    {selectedPatient.age ? ` · ${selectedPatient.age} tuổi` : ''}{selectedPatient.gender ? ` · ${GENDER_LABEL[selectedPatient.gender] || selectedPatient.gender}` : ''} · Giường {selectedPatient.bedNumber}
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  MIT-BIH #{selectedPatient.activeRecordId} · Phiên <SessionDuration startedAt={sessionStartedAt} /> · {totalBeats} nhịp đã phân tích
                </div>
              </div>
            </div>
          ) : (
            <h2 style={{ margin: 0, fontSize: '15px', color: 'var(--text-muted)', fontWeight: '600' }}>Chưa chọn bệnh nhân theo dõi</h2>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {selectedPatient && <AlarmStatus connectionStatus={connectionStatus} />}
            {selectedPatient && <MuteButton />}
            {selectedPatient && <div style={{ width: '1px', height: '26px', backgroundColor: 'var(--border-color)' }} />}
            {selectedPatient && <ReportButton chartElementRef={chartRef} />}
            <ToolbarButton icon="🧪" label="Chẩn đoán offline (CSV)" onClick={() => setIsModalOpen(true)} />
          </div>
        </div>

        {selectedPatient && (
          <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', display: 'flex', gap: '18px', flexWrap: 'wrap', paddingLeft: '52px' }}>
            <span>🕒 <LiveClock /></span>
            <span>Ngưỡng lọc AI: <strong style={{ color: 'var(--text-main)' }}>{confidenceThreshold ? `${Math.round(confidenceThreshold * 100)}%` : 'Không lọc'}</strong></span>
            {/* Độ trễ xử lý là chỉ số HIỆU NĂNG HỆ THỐNG (không phải thông tin bệnh nhân) - đặt
                cùng hàng meta nhỏ/mờ này thay vì thẻ riêng to bằng BPM/HRV, để không đánh lạc
                hướng bác sĩ khỏi các chỉ số lâm sàng thật sự cần ra quyết định. */}
            <span title="Thời gian từ lúc phát hiện đỉnh R đến khi gửi kết quả - chỉ số hiệu năng hệ thống">
              Độ trễ hệ thống: <strong style={{ color: latencyE2e > 2000 ? 'var(--danger)' : 'var(--text-main)' }}>{latencyE2e ? `${latencyE2e.toFixed(0)} ms` : '--'}</strong>
            </span>
          </div>
        )}
      </div>

      <UploadDiagnosisModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

      {!selectedPatient ? (
        // Đúng luồng lâm sàng: phải biết đang theo dõi bệnh nhân nào trước khi hiện ECG,
        // không tự stream 1 bản ghi mặc định vô danh như trước nữa.
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '14px', padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '40px' }}>🏥</div>
          <h3 style={{ margin: 0, color: 'var(--text-main)' }}>Chưa chọn bệnh nhân để theo dõi</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '14px', maxWidth: '420px' }}>
            Chọn 1 bệnh nhân đang quản lý để bắt đầu xem tín hiệu ECG thời gian thực của người đó.
          </p>
          {patients.length > 0 ? (
            <select
              defaultValue=""
              onChange={(e) => {
                const p = patients.find(x => String(x.id) === e.target.value);
                if (p) setSelectedPatient(p);
              }}
              style={{ padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-main)', fontSize: '14px', minWidth: '260px' }}
            >
              <option value="" disabled>-- Chọn bệnh nhân --</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.name} · Giường {p.bedNumber}</option>
              ))}
            </select>
          ) : (
            <>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '13px' }}>
                Chưa có bệnh nhân nào trong hệ thống. Thêm tay qua "Hồ Sơ Bệnh Nhân", hoặc tạo
                nhanh 1 bệnh nhân mẫu cho mỗi bản ghi ECG có sẵn để dùng thử ngay:
              </p>
              <button
                type="button"
                onClick={handleSeedDemoPatients}
                disabled={isSeeding}
                style={{
                  padding: '10px 18px', borderRadius: '8px', border: 'none',
                  backgroundColor: 'var(--primary)', color: 'white', fontWeight: '600',
                  fontSize: '13.5px', cursor: isSeeding ? 'default' : 'pointer',
                  opacity: isSeeding ? 0.7 : 1,
                }}
              >
                {isSeeding ? 'Đang tạo...' : '＋ Tạo bệnh nhân mẫu từ các bản ghi có sẵn'}
              </button>
            </>
          )}
          {seedError && (
            <p style={{ margin: 0, color: 'var(--danger)', fontSize: '12.5px' }}>{seedError}</p>
          )}
        </div>
      ) : isInitialLoading ? (
        <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <StatCards
            latestPrediction={latestPrediction}
            currentAlarmLevel={currentAlarmLevel}
            currentAlarmLabel={currentAlarmLabel}
            bpm={bpm}
            hrv_sdnn={hrvSdnn}
            hrv_rmssd={hrvRmssd}
            confidence={confidence}
            afibSuspected={afibSuspected}
            afibScore={afibScore}
            tachycardiaSuspected={tachycardiaSuspected}
          />
          <div ref={chartRef} style={{ display: 'flex', flex: 1, minHeight: '0', position: 'relative' }}>
            <ECGChart xData={xData} yData={yData} yData2={yData2} lead1Name={lead1Name} lead2Name={lead2Name} heatmap={currentHeatmap} />
          </div>
        </>
      )}
    </div>
  );
};

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

// Cụm trạng thái hợp nhất: mức cảnh báo (màu sắc mạnh, đúng phân cấp - đây mới là thứ quan
// trọng nhất trên toàn thanh công cụ) + trạng thái kết nối gộp làm 1 pill duy nhất, thay vì 2
// khối tách rời như trước (badge tròn riêng + dòng chữ "● Đã kết nối" trôi nổi riêng).
const AlarmStatus = ({ connectionStatus }) => {
  const { currentAlarmLevel } = useAlarm();
  const isDanger = currentAlarmLevel >= 3;
  const isWarning = currentAlarmLevel === 2;
  const color = isDanger ? 'var(--danger)' : isWarning ? 'var(--warning)' : 'var(--success)';
  const levelText = isDanger ? 'Cấp 3 · Khẩn cấp' : isWarning ? 'Cấp 2 · Cảnh báo' : 'Bình thường';
  const isConnected = connectionStatus === 'Đã kết nối';

  return (
    <div
      className={isDanger ? 'pulse-log-danger' : undefined}
      style={{
        display: 'flex', alignItems: 'center', gap: 10, padding: '7px 14px', borderRadius: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : isWarning ? 'rgba(245,158,11,0.12)' : 'var(--card-bg)',
        border: `1px solid ${color}`,
      }}
    >
      <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: color, flexShrink: 0 }} />
      <span style={{ fontSize: 13, color, fontWeight: 700 }}>{levelText}</span>
      <span style={{ width: '1px', height: '14px', backgroundColor: 'var(--border-color)' }} />
      <span style={{ fontSize: 12, color: isConnected ? 'var(--text-muted)' : 'var(--danger)', fontWeight: 500, whiteSpace: 'nowrap' }}>
        {isConnected ? '● Đã kết nối' : `⚠ ${connectionStatus}`}
      </span>
    </div>
  );
};

// Nút tắt tiếng cảnh báo ngay trên màn hình theo dõi - trước đây chức năng này chỉ có trong
// Cài Đặt Hệ Thống, nhưng trang đó vừa bị khoá admin-only nên bác sĩ/y tá đang trực không còn
// cách nào tắt còi khẩn cấp. Logic mute/unmute (tự bật lại sau 2 phút, chuẩn IEC 60601-1-8)
// giữ nguyên trong AlarmContext, ở đây chỉ là 1 nút gọn dùng lại state có sẵn.
const MuteButton = () => {
  const { isMuted, snoozeCountdown, muteAlarm, unmuteAlarm } = useAlarm();

  if (isMuted) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '7px 8px 7px 14px', borderRadius: '8px', backgroundColor: 'var(--card-bg)', border: '1px solid var(--warning)' }}>
        <span style={{ fontSize: 13, color: 'var(--warning)', fontWeight: 600 }}>
          🔇 {Math.floor(snoozeCountdown / 60)}:{String(snoozeCountdown % 60).padStart(2, '0')}
        </span>
        <button
          onClick={unmuteAlarm}
          style={{ padding: '4px 11px', backgroundColor: 'var(--success)', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}
        >
          🔔 Bật lại
        </button>
      </div>
    );
  }

  return <ToolbarButton icon="🔇" label="Tắt tiếng 2 phút" onClick={muteAlarm} title="Tắt tiếng cảnh báo trong 2 phút" tone="warning" />;
};

// Hệ nút hành động phụ dùng CHUNG 1 kiểu (viền mảnh + icon + nhãn) cho mọi hành động thứ cấp
// trên toolbar (xuất báo cáo, chẩn đoán offline...) - trước đây mỗi nút tự chọn màu nền đặc
// riêng (xanh lá, xanh dương...) khiến chúng trông như đến từ nhiều bộ giao diện khác nhau.
const ToolbarButton = ({ icon, label, onClick, title, tone = 'default' }) => {
  const toneColor = tone === 'warning' ? 'var(--warning)' : 'var(--text-main)';
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      style={{
        display: 'flex', alignItems: 'center', gap: '7px',
        padding: '7px 14px', borderRadius: '8px', cursor: 'pointer',
        backgroundColor: 'transparent', border: `1px solid ${tone === 'warning' ? 'var(--warning)' : 'var(--border-color)'}`,
        color: toneColor, fontWeight: '600', fontSize: '13px',
        transition: 'background-color 0.15s ease',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-color)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
    >
      <span>{icon}</span>
      {label}
    </button>
  );
};

// Đồng hồ thời gian thực nhỏ gọn - tách riêng để chỉ đúng phần này re-render mỗi giây,
// không kéo theo toàn bộ thanh trạng thái phía trên vẽ lại 60 lần/phút.
const LiveClock = () => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);
  return new Date(now).toLocaleTimeString('vi-VN');
};

// Thời lượng phiên theo dõi (mm:ss) - tách riêng cùng lý do với LiveClock ở trên.
const SessionDuration = ({ startedAt }) => {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);
  const elapsedSec = startedAt ? Math.max(0, Math.floor((now - startedAt) / 1000)) : 0;
  return `${Math.floor(elapsedSec / 60)}:${String(elapsedSec % 60).padStart(2, '0')}`;
};

export default DashboardPage;
