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
    latency,
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

      {/* Thanh công cụ */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {selectedPatient && <AlarmStatus />}
          {selectedPatient && <MuteButton />}
          {selectedPatient && (
            <span style={{ fontSize: '14px', color: connectionStatus === 'Đã kết nối' ? '#10b981' : 'var(--danger)' }}>
              ● {connectionStatus}
            </span>
          )}
          {selectedPatient && <ReportButton chartElementRef={chartRef} />}
          <button
            onClick={() => setIsModalOpen(true)}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--primary)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Chẩn đoán offline (CSV)
          </button>
        </div>
      </div>

      <UploadDiagnosisModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />

      {selectedPatient && (
        <SessionInfoBar
          patient={selectedPatient}
          sessionStartedAt={sessionStartedAt}
          totalBeats={totalBeats}
          confidenceThreshold={confidenceThreshold}
        />
      )}

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
            latency={latency}
            latencyE2e={latencyE2e}
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

// Badge cấp cảnh báo hiện tại - chỉ hiện trong lúc theo dõi 1 bệnh nhân (không đặt ở Header
// nữa vì ngoài lúc theo dõi nhịp tim, mức cảnh báo chưa có ý nghĩa gì để hiện mọi lúc).
const AlarmStatus = () => {
  const { currentAlarmLevel } = useAlarm();
  const levelIcon = currentAlarmLevel >= 3 ? '🔴' : (currentAlarmLevel === 2 ? '🟡' : '🟢');
  const levelText = currentAlarmLevel >= 3 ? 'Cấp 3' : (currentAlarmLevel === 2 ? 'Cấp 2' : 'Bình thường');

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 12px', borderRadius: '6px', backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)' }}>
      <div style={{ fontSize: 16 }}>{levelIcon}</div>
      <div style={{ fontSize: 13, color: currentAlarmLevel >= 3 ? '#ef4444' : (currentAlarmLevel === 2 ? '#f59e0b' : '#10b981'), fontWeight: 600 }}>{levelText}</div>
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
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 12px', borderRadius: '6px', backgroundColor: 'var(--card-bg)', border: '1px solid var(--warning)' }}>
        <span style={{ fontSize: 13, color: 'var(--warning)', fontWeight: 600 }}>
          🔇 {Math.floor(snoozeCountdown / 60)}:{String(snoozeCountdown % 60).padStart(2, '0')}
        </span>
        <button
          onClick={unmuteAlarm}
          style={{ padding: '3px 10px', backgroundColor: 'var(--success)', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}
        >
          🔔 Bật lại
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={muteAlarm}
      title="Tắt tiếng cảnh báo trong 2 phút"
      style={{ padding: '6px 12px', backgroundColor: 'transparent', color: 'var(--warning)', border: '1px solid var(--warning)', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '600' }}
    >
      🔇 Tắt tiếng 2 phút
    </button>
  );
};

const GENDER_LABEL = { M: 'Nam', F: 'Nữ', Other: 'Khác' };

// Dải thông tin phiên theo dõi - gộp định danh bệnh nhân (giống cách máy ECG giấy luôn in
// patient info ngay trên bản ghi), đồng hồ thời gian thực, thời lượng phiên và tổng số nhịp đã
// phân tích, cùng ngưỡng lọc cảnh báo AI hiện tại (đọc được mà không cần vào Cài Đặt, giờ đã
// admin-only). Thay cho dòng "Đang theo dõi: X" đơn giản trước đây.
const SessionInfoBar = ({ patient, sessionStartedAt, totalBeats, confidenceThreshold }) => {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, []);

  const elapsedSec = sessionStartedAt ? Math.max(0, Math.floor((now - sessionStartedAt) / 1000)) : 0;
  const durationText = `${Math.floor(elapsedSec / 60)}:${String(elapsedSec % 60).padStart(2, '0')}`;
  const clockText = new Date(now).toLocaleTimeString('vi-VN');
  const thresholdText = confidenceThreshold ? `${Math.round(confidenceThreshold * 100)}%` : 'Không lọc';

  return (
    <div className="card" style={{ padding: '10px 20px', display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px 24px', fontSize: '12.5px' }}>
      <div style={{ color: 'var(--text-main)', fontWeight: '600' }}>
        🧑‍⚕️ {patient.name}{patient.age ? ` · ${patient.age} tuổi` : ''}{patient.gender ? ` · ${GENDER_LABEL[patient.gender] || patient.gender}` : ''} · Giường {patient.bedNumber}
      </div>
      <div style={{ color: 'var(--text-muted)' }}>
        Bản ghi: <strong style={{ color: 'var(--text-main)' }}>MIT-BIH #{patient.activeRecordId}</strong>
      </div>
      <div style={{ color: 'var(--text-muted)' }}>
        🕒 {clockText}
      </div>
      <div style={{ color: 'var(--text-muted)' }}>
        Thời lượng phiên: <strong style={{ color: 'var(--text-main)' }}>{durationText}</strong>
      </div>
      <div style={{ color: 'var(--text-muted)' }}>
        Tổng nhịp đã phân tích: <strong style={{ color: 'var(--text-main)' }}>{totalBeats}</strong>
      </div>
      <div style={{ color: 'var(--text-muted)' }}>
        Ngưỡng lọc AI: <strong style={{ color: 'var(--text-main)' }}>{thresholdText}</strong>
      </div>
    </div>
  );
};

export default DashboardPage;
