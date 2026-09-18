import React, { useState, useEffect } from 'react';
import StatCards from '../components/dashboard/StatCards';
import ECGChart from '../components/dashboard/ECGChart';
import LoadingSpinner from '../components/dashboard/LoadingSpinner';
import RecordSelector from '../components/dashboard/RecordSelector';
import UploadDiagnosisModal from '../components/dashboard/UploadDiagnosisModal';
import { useAnomaly } from '../context/AnomalyContext';
import { usePatient } from '../context/PatientContext';
import { useAlarm } from '../context/AlarmContext';
import { loadSettings } from './SettingsPage';
import { useAuth } from '../context/AuthContext';

const MAX_POINTS = 1000;

const DashboardPage = () => {
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  
  const [xData, setXData] = useState([]);
  const [yData, setYData] = useState([]);
  const [currentHeatmap, setCurrentHeatmap] = useState(null);
  
  const [latestPrediction, setLatestPrediction] = useState('Đang tải...');
  const [latency, setLatency] = useState(0);
  const [bpm, setBpm] = useState(null);
  const [hrvSdnn, setHrvSdnn] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [afibSuspected, setAfibSuspected] = useState(false);
  const [afibScore, setAfibScore] = useState(0);
  const [tachycardiaSuspected, setTachycardiaSuspected] = useState(false);

  const [localSelectedRecord, setLocalSelectedRecord] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

    const { addAnomaly } = useAnomaly();
  const { selectedPatient } = usePatient();
  const { triggerAlarm } = useAlarm();
  const { getWsTicket } = useAuth(); // Import getWsTicket

  // handleNewData sống bên trong 1 useEffect hiếm khi chạy lại (chỉ khi đổi record/bệnh
  // nhân/wsUrl) - nếu gọi thẳng triggerAlarm/addAnomaly, closure sẽ đóng băng bản cũ mãi mãi
  // (vd sau khi bấm Mute, AlarmContext tạo lại triggerAlarm mới nhưng handleNewData vẫn gọi
  // bản cũ tưởng chưa mute). Dùng ref để luôn lấy đúng bản mới nhất mà không phải thêm vào
  // dependency array của effect (thêm vào sẽ làm WS bị đóng/mở lại mỗi lần trạng thái mute đổi).
  const triggerAlarmRef = React.useRef(triggerAlarm);
  const addAnomalyRef = React.useRef(addAnomaly);
  useEffect(() => {
    triggerAlarmRef.current = triggerAlarm;
    addAnomalyRef.current = addAnomaly;
  }, [triggerAlarm, addAnomaly]);

  // Đọc settings để lấy wsUrl và confidenceThreshold
  const [settings, setSettings] = useState(loadSettings());
  useEffect(() => {
    // Để ý nếu localStorage thay đổi thì update
    const interval = setInterval(() => setSettings(loadSettings()), 1000);
    return () => clearInterval(interval);
  }, []);
  
  // Ưu tiên bản ghi của bệnh nhân active
  const selectedRecord = selectedPatient ? selectedPatient.activeRecordId : localSelectedRecord;
  
  // Ref cho báo cáo PDF
  const chartRef = React.useRef(null);

  // Giữ bản sao yData mới nhất ngoài React state - handleNewData được định nghĩa 1 lần mỗi
  // khi effect WS chạy lại (không phải mỗi lần render), nên closure `yData` lấy trực tiếp từ
  // useState sẽ bị "đóng băng" ở giá trị lúc effect khởi chạy, không cập nhật theo từng nhịp.
  // Trước đây dùng setYData(prev => {...}) để né việc này, nhưng lại gọi addAnomalyRef.current()
  // (setState của AnomalyContext) NGAY BÊN TRONG updater function đó - React cảnh báo "Cannot
  // update a component while rendering a different component" vì updater có thể bị gọi lại
  // (đặc biệt StrictMode) làm log trùng anomaly. Dùng ref đọc/ghi trực tiếp, gọi setYData với
  // giá trị đã tính sẵn (không phải updater function) - không còn side effect nào bên trong.
  const yDataRef = React.useRef([]);
  const xDataRef = React.useRef([]);

  // Backend gửi 36 gói tin/giây (đúng tốc độ gốc MIT-BIH 360Hz) - setXData/setYData trước đây
  // gọi trực tiếp trong handleNewData nên Plotly re-render 36 lần/giây, tốn CPU không cần thiết
  // (mắt người không phân biệt được khác biệt giữa 36fps và ~15fps trên 1 đường line chart).
  // Giờ handleNewData chỉ ghi vào ref (rẻ), còn setState thật được dồn lại và "xả" theo chu kỳ
  // cố định ở đây - giảm số lần Plotly redraw mà tốc độ hiển thị cảm nhận được không đổi.
  useEffect(() => {
    const flushInterval = setInterval(() => {
      setXData(xDataRef.current);
      setYData(yDataRef.current);
    }, 66);
    return () => clearInterval(flushInterval);
  }, []);

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;
    let cancelled = false; // true khi effect này bị cleanup (đổi bản ghi/unmount) - chặn onclose cũ tự reconnect lại bản ghi cũ

    // Reset toàn bộ dữ liệu hiển thị mỗi khi effect này CHẠY LẠI (đổi bản ghi/bệnh nhân/wsUrl) -
    // trước đây chỉ reset xData/yData/heatmap, và CHỈ khi mất kết nối thật (ws.onclose có guard
    // `if (cancelled) return`, mà lúc đổi bản ghi cleanup luôn set cancelled=true TRƯỚC khi gọi
    // ws.close(), nên nhánh reset đó không bao giờ chạy lúc đổi bản ghi). Hậu quả: đổi từ 1 bản
    // ghi đang có badge AFib/tachycardia/cảnh báo đỏ sang bản ghi khác (kể cả bản ghi "bình
    // thường") vẫn hiện nguyên các badge/cảnh báo CŨ vài giây cho tới khi có nhịp đầu tiên của
    // bản ghi mới. Reset ngay ở đây thay vì dựa vào onclose.
    setIsInitialLoading(true);
    setXData([]);
    setYData([]);
    yDataRef.current = [];
    xDataRef.current = [];
    setCurrentHeatmap(null);
    setLatestPrediction('Đang tải...');
    setLatency(0);
    setBpm(null);
    setHrvSdnn(null);
    setConfidence(null);
    setAfibSuspected(false);
    setAfibScore(0);
    setTachycardiaSuspected(false);
    triggerAlarmRef.current('BÌNH THƯỜNG', 0, 1); // tắt còi/badge cảnh báo của bản ghi cũ ngay lập tức

    const handleNewData = (data) => {
      const { chunk, prediction, latency_ms, heatmap, anomaly_id, bpm, hrv_sdnn, confidence, afib_suspected, afib_score, tachycardia_suspected, is_new_beat } = data;
      
      setLatency(latency_ms);
      setLatestPrediction(prediction);
      if (bpm !== undefined) setBpm(bpm);
      if (hrv_sdnn !== undefined) setHrvSdnn(hrv_sdnn);
      if (confidence !== undefined) setConfidence(confidence);
      if (afib_suspected !== undefined) setAfibSuspected(afib_suspected);
      if (afib_score !== undefined) setAfibScore(afib_score);
      if (tachycardia_suspected !== undefined) setTachycardiaSuspected(tachycardia_suspected);
      
      if (is_new_beat) {
        // Gọi trigger alarm mỗi khi có 1 nhịp mới - kể cả lúc AAMI là Bình thường (heatmap
        // null), vì afib_suspected/tachycardia_suspected có thể đang true độc lập với nhãn
        // AAMI của đúng nhịp này (rung nhĩ/nhịp nhanh là điều kiện theo nhịp điệu nhiều nhịp,
        // không phải hình dạng riêng 1 nhịp) - nếu chỉ gọi lúc có heatmap sẽ bỏ lỡ 2 cảnh báo
        // này hoàn toàn khi nhịp hiện tại được phân loại Bình thường.
        triggerAlarmRef.current(prediction, settings.confidenceThreshold, confidence, {
          afibSuspected: afib_suspected,
          tachycardiaSuspected: tachycardia_suspected,
        });
      }

      // Tính yData mới dựa trên ref (luôn mới nhất), không dùng updater function của setYData
      // nữa - xem giải thích ở khai báo yDataRef.current phía trên.
      const rawY = [...yDataRef.current, ...chunk];
      const nextY = rawY.length > MAX_POINTS ? rawY.slice(rawY.length - MAX_POINTS) : rawY;
      yDataRef.current = nextY;

      if (heatmap) {
        setCurrentHeatmap(heatmap);

        if (prediction && prediction.includes('CẢNH BÁO')) {
          // Lưu lại chính xác 187 điểm cuối cùng (trước khi cắt bớt theo MAX_POINTS) để XAI phân tích
          const recent187 = rawY.slice(-187);
          addAnomalyRef.current({
            prediction,
            latency: latency_ms,
            heatmap: heatmap,
            confidence: confidence, // Lưu thêm confidence
            signal: recent187.length === 187 ? recent187 : null, // Chỉ lấy khi đủ 187
            anomalyId: anomaly_id, // id AnomalyEvent thật trong DB - dùng để bác sĩ xác nhận/sửa nhãn (XAIPage)
            reviewStatus: 'pending',
          });
        }
      } else {
        setCurrentHeatmap(null);
      }
      
      const prevX = xDataRef.current;
      const lastX = prevX.length > 0 ? prevX[prevX.length - 1] : 0;
      const newXChunks = Array.from({length: chunk.length}, (_, i) => lastX + i + 1);
      const rawX = [...prevX, ...newXChunks];
      xDataRef.current = rawX.length > MAX_POINTS ? rawX.slice(rawX.length - MAX_POINTS) : rawX;
    };

    const connect = async () => {
      if (ws) {
        try { ws.close(); } catch (e) {}
      }

      const base = `${settings.wsUrl}/ws/ecg`;
      let qs = '';
      if (selectedRecord) qs += `?record=${selectedRecord}`;
      if (selectedPatient?.remoteId) qs += `${qs ? '&' : '?'}patient_id=${selectedPatient.remoteId}`;
      
      try {
        const ticket = await getWsTicket();
        if (cancelled) return;
        if (ticket) qs += `${qs ? '&' : '?'}ticket=${encodeURIComponent(ticket)}`;
      } catch (err) {
        console.error('Không thể lấy WS ticket:', err);
        if (cancelled) return;
        setConnectionStatus('Phiên đăng nhập lỗi, đang thử lại...');
        reconnectTimeout = setTimeout(connect, 3000);
        return;
      }

      const wsUrl = base + qs;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (cancelled) return;
        setConnectionStatus('Đã kết nối');
        setIsInitialLoading(false);
      };

      ws.onmessage = (event) => {
        if (cancelled) return;
        try {
          const data = JSON.parse(event.data);
          handleNewData(data);
        } catch (err) {
          console.error('Lỗi giải mã JSON WebSocket:', err);
        }
      };

      ws.onclose = (event) => {
        if (cancelled) return;
        setConnectionStatus(event?.code === 4401 ? 'Phiên đăng nhập hết hạn, đang thử lại...' : 'Đang kết nối lại...');
        xDataRef.current = [];
        yDataRef.current = [];
        setXData([]);
        setYData([]);
        setCurrentHeatmap(null);

        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error('Lỗi WebSocket:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [selectedRecord, selectedPatient, settings.wsUrl]); // Chạy lại hiệu ứng khi bản ghi, bệnh nhân hoặc wsUrl thay đổi

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      
      {/* Thanh công cụ */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ flex: 1 }}>
          <RecordSelector 
            selectedRecord={localSelectedRecord} 
            onSelectRecord={setLocalSelectedRecord} 
          />
          {selectedPatient && (
            <div style={{ fontSize: '13px', color: '#f59e0b', marginTop: '6px' }}>
              ⚠️ Đang khóa ở bản ghi của bệnh nhân: <strong>{selectedPatient.name}</strong>
            </div>
          )}
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ fontSize: '14px', color: connectionStatus === 'Đã kết nối' ? '#10b981' : 'var(--danger)' }}>
            ● {connectionStatus}
          </span>
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

      {isInitialLoading ? (
        <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <StatCards 
            latestPrediction={latestPrediction} 
            latency={latency} 
            bpm={bpm}
            hrv_sdnn={hrvSdnn}
            confidence={confidence}
            afibSuspected={afibSuspected}
            afibScore={afibScore}
            tachycardiaSuspected={tachycardiaSuspected}
          />
          <div ref={chartRef} style={{ display: 'flex', flex: 1, minHeight: '0', position: 'relative' }}>
            <ECGChart xData={xData} yData={yData} heatmap={currentHeatmap} />
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardPage;
