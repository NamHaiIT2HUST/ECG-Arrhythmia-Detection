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

  const [localSelectedRecord, setLocalSelectedRecord] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { addAnomaly } = useAnomaly();
  const { selectedPatient } = usePatient();
  const { triggerAlarm } = useAlarm();

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

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;
    let cancelled = false; // true khi effect này bị cleanup (đổi bản ghi/unmount) - chặn onclose cũ tự reconnect lại bản ghi cũ

    const handleNewData = (data) => {
      const { chunk, prediction, latency_ms, heatmap, bpm, hrv_sdnn, confidence } = data;
      
      setLatency(latency_ms);
      setLatestPrediction(prediction);
      if (bpm !== undefined) setBpm(bpm);
      if (hrv_sdnn !== undefined) setHrvSdnn(hrv_sdnn);
      if (confidence !== undefined) setConfidence(confidence);
      
      if (heatmap) {
        setCurrentHeatmap(heatmap);

        // Gọi trigger alarm cho tất cả các bản tin có prediction (kể cả bình thường để tắt alarm)
        triggerAlarmRef.current(prediction, settings.confidenceThreshold, confidence);

        if (prediction && prediction.includes('CẢNH BÁO')) {
          // Lưu lại chính xác 187 điểm cuối cùng của yData (và thêm chunk) để XAI phân tích
          setYData(prevY => {
            const tempY = [...prevY, ...chunk];
            const recent187 = tempY.slice(-187);

            // Đẩy vào context
            addAnomalyRef.current({
              prediction,
              latency: latency_ms,
              heatmap: heatmap,
              confidence: confidence, // Lưu thêm confidence
              signal: recent187.length === 187 ? recent187 : null // Chỉ lấy khi đủ 187
            });
            
            return tempY.length > MAX_POINTS ? tempY.slice(tempY.length - MAX_POINTS) : tempY;
          });
        }
      } else {
        setCurrentHeatmap(null);
        setYData(prevY => {
          const newY = [...prevY, ...chunk];
          if (newY.length > MAX_POINTS) return newY.slice(newY.length - MAX_POINTS);
          return newY;
        });
      }
      
      setXData(prevX => {
        const lastX = prevX.length > 0 ? prevX[prevX.length - 1] : 0;
        const newXChunks = Array.from({length: chunk.length}, (_, i) => lastX + i + 1);
        const newX = [...prevX, ...newXChunks];
        if (newX.length > MAX_POINTS) return newX.slice(newX.length - MAX_POINTS);
        return newX;
      });
    };

    const connect = () => {
      if (ws) {
        try { ws.close(); } catch (e) {}
      }

      // Khởi tạo WS URL từ settings, nếu có selectedRecord thì truyền vào query
      const base = `${settings.wsUrl}/ws/ecg`;
      let qs = '';
      if (selectedRecord) qs += `?record=${selectedRecord}`;
      // Backend yêu cầu patient_id là số nguyên (id thật trong bảng `patients`). Bệnh nhân chỉ
      // lưu localStorage (chưa có API /api/patients thật) có `id` là UUID (crypto.randomUUID())
      // - gửi UUID này sẽ làm FastAPI từ chối handshake WS ngay lúc validate query param. Chỉ
      // truyền patient_id khi đã có remoteId (số nguyên, đồng bộ từ backend thật); nếu chưa có,
      // bỏ qua tham số này - backend tự dùng "bệnh nhân mặc định" (xem plan.md mục 5.4).
      if (selectedPatient?.remoteId) qs += `${qs ? '&' : '?'}patient_id=${selectedPatient.remoteId}`;
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

      ws.onclose = () => {
        if (cancelled) return; // effect đã bị cleanup (vd đổi bản ghi) - đây không phải mất kết nối thật, đừng tự reconnect lại bản ghi cũ
        setConnectionStatus('Đang kết nối lại...');
        // Reset buffers
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
