import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAnomaly } from './AnomalyContext';
import { usePatient } from './PatientContext';
import { useAlarm } from './AlarmContext';
import { useAuth } from './AuthContext';
import { loadSettings } from '../pages/SettingsPage';
import { resolveWsBase } from '../utils/serverUrl';

const MonitoringContext = createContext();

export const useMonitoring = () => useContext(MonitoringContext);

// 3600 diem = 10 giay o 360Hz (toc do goc MIT-BIH, xem data_streamer.py) - voi nhip nghi
// ~70-90 bpm se hien ~8-12 chu ky tim tren 1 khung hinh, dung khuyen nghi tu bac si tham
// khao (may ECG that thuong hien 8-10 chu ky/man hinh, ít hon se lam so BPM tuc thoi trong
// "nhay loan" vi qua it ngu canh).
const MAX_POINTS = 3600;

// Chuyển từ DashboardPage.jsx sang đây để phiên theo dõi (socket + buffer dữ liệu) sống ở
// cấp Provider, không bị unmount/reset mỗi khi bác sĩ chuyển sang tab khác rồi quay lại
// "Theo Dõi Trực Tuyến" - trước đây DashboardPage tự mở/đóng socket trong useEffect của
// chính nó nên rời tab là mất hết dữ liệu đang xem.
export const MonitoringProvider = ({ children }) => {
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  const [xData, setXData] = useState([]);
  const [yData, setYData] = useState([]);
  const [yData2, setYData2] = useState([]);
  const [lead1Name, setLead1Name] = useState(null);
  const [lead2Name, setLead2Name] = useState(null);
  const [currentHeatmap, setCurrentHeatmap] = useState(null);

  const [latestPrediction, setLatestPrediction] = useState('Đang tải...');
  const [latency, setLatency] = useState(0);
  const [latencyE2e, setLatencyE2e] = useState(0);
  const [bpm, setBpm] = useState(null);
  const [hrvSdnn, setHrvSdnn] = useState(null);
  const [hrvRmssd, setHrvRmssd] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [afibSuspected, setAfibSuspected] = useState(false);
  const [afibScore, setAfibScore] = useState(0);
  const [tachycardiaSuspected, setTachycardiaSuspected] = useState(false);
  const [sessionStartedAt, setSessionStartedAt] = useState(null);
  const [totalBeats, setTotalBeats] = useState(0);

  const { addAnomaly, clearHistory } = useAnomaly();
  const { selectedPatient } = usePatient();
  const { triggerAlarm } = useAlarm();
  const { getWsTicket, isAuthenticated } = useAuth();

  // handleNewData sống bên trong 1 useEffect hiếm khi chạy lại (chỉ khi đổi record/bệnh
  // nhân/wsUrl) - nếu gọi thẳng triggerAlarm/addAnomaly, closure sẽ đóng băng bản cũ mãi mãi
  // (vd sau khi bấm Mute, AlarmContext tạo lại triggerAlarm mới nhưng handleNewData vẫn gọi
  // bản cũ tưởng chưa mute). Dùng ref để luôn lấy đúng bản mới nhất mà không phải thêm vào
  // dependency array của effect (thêm vào sẽ làm WS bị đóng/mở lại mỗi lần trạng thái mute đổi).
  const triggerAlarmRef = useRef(triggerAlarm);
  const addAnomalyRef = useRef(addAnomaly);
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

  // Bat buoc phai co benh nhan dang chon moi co ban ghi de stream (xem khoi "chua chon
  // benh nhan" o DashboardPage) - moi benh nhan tao qua PatientForm deu da co san activeRecordId.
  const selectedRecord = selectedPatient?.activeRecordId;

  // Giữ bản sao yData mới nhất ngoài React state - handleNewData được định nghĩa 1 lần mỗi
  // khi effect WS chạy lại (không phải mỗi lần render), nên closure `yData` lấy trực tiếp từ
  // useState sẽ bị "đóng băng" ở giá trị lúc effect khởi chạy, không cập nhật theo từng nhịp.
  // Trước đây dùng setYData(prev => {...}) để né việc này, nhưng lại gọi addAnomalyRef.current()
  // (setState của AnomalyContext) NGAY BÊN TRONG updater function đó - React cảnh báo "Cannot
  // update a component while rendering a different component" vì updater có thể bị gọi lại
  // (đặc biệt StrictMode) làm log trùng anomaly. Dùng ref đọc/ghi trực tiếp, gọi setYData với
  // giá trị đã tính sẵn (không phải updater function) - không còn side effect nào bên trong.
  const yDataRef = useRef([]);
  const yData2Ref = useRef([]);
  const xDataRef = useRef([]);

  // Backend gửi 36 gói tin/giây (đúng tốc độ gốc MIT-BIH 360Hz) - setXData/setYData trước đây
  // gọi trực tiếp trong handleNewData nên Plotly re-render 36 lần/giây, tốn CPU không cần thiết
  // (mắt người không phân biệt được khác biệt giữa 36fps và ~15fps trên 1 đường line chart).
  // Giờ handleNewData chỉ ghi vào ref (rẻ), còn setState thật được dồn lại và "xả" theo chu kỳ
  // cố định ở đây - giảm số lần Plotly redraw mà tốc độ hiển thị cảm nhận được không đổi.
  useEffect(() => {
    const flushInterval = setInterval(() => {
      setXData(xDataRef.current);
      setYData(yDataRef.current);
      setYData2(yData2Ref.current);
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
    setYData2([]);
    setLead1Name(null);
    setLead2Name(null);
    yDataRef.current = [];
    yData2Ref.current = [];
    xDataRef.current = [];
    setCurrentHeatmap(null);
    setLatestPrediction('Đang tải...');
    setLatency(0);
    setLatencyE2e(0);
    setBpm(null);
    setHrvSdnn(null);
    setHrvRmssd(null);
    setConfidence(null);
    setAfibSuspected(false);
    setAfibScore(0);
    setTachycardiaSuspected(false);
    // Đổi bệnh nhân/bản ghi = bắt đầu 1 phiên theo dõi mới - đặt lại mốc giờ bắt đầu và số nhịp
    // đã phân tích, để dải thông tin phiên trên Dashboard không cộng dồn nhầm giữa 2 bệnh nhân.
    setSessionStartedAt(selectedPatient ? Date.now() : null);
    setTotalBeats(0);
    triggerAlarmRef.current('BÌNH THƯỜNG', 0, 1); // tắt còi/badge cảnh báo của bản ghi cũ ngay lập tức
    // Đổi bệnh nhân/bản ghi = phiên theo dõi mới - xoá luôn lịch sử cảnh báo của bệnh nhân cũ,
    // nếu không trang XAI/Báo cáo sẽ lẫn cảnh báo của nhiều bệnh nhân khác nhau trong cùng 1
    // phiên trình duyệt (trước đây không có bước này vì state stream còn nằm trong
    // DashboardPage, chưa cần phân biệt "phiên theo dõi của ai" rõ ràng như bây giờ).
    clearHistory();

    // Chưa đăng nhập - đừng cố mở WS (sẽ luôn 401/retry vô ích). MonitoringProvider nằm phía
    // trên cả kiểm tra isAuthenticated trong App.jsx để sống sót qua mọi lần đổi tab, nên phải
    // tự chờ đăng nhập xong ở đây thay vì dựa vào việc component cha có bị unmount hay không.
    // Chưa chọn bệnh nhân nào - không tự stream 1 bản ghi mặc định nữa (đúng luồng lâm sàng:
    // phải biết đang theo dõi ai trước). Dừng ở đây, DashboardPage sẽ hiện khối "chọn bệnh nhân".
    if (!isAuthenticated || !selectedPatient) {
      setIsInitialLoading(false);
      return () => { cancelled = true; };
    }

    const handleNewData = (data) => {
      const { chunk, chunk2, lead1_name, lead2_name, prediction, latency_ms, latency_e2e_ms, heatmap, anomaly_id, bpm, hrv_sdnn, hrv_rmssd, confidence, afib_suspected, afib_score, tachycardia_suspected, is_new_beat } = data;

      if (lead1_name !== undefined) setLead1Name(lead1_name);
      if (lead2_name !== undefined) setLead2Name(lead2_name);
      setLatency(latency_ms);
      if (latency_e2e_ms !== undefined) setLatencyE2e(latency_e2e_ms);
      setLatestPrediction(prediction);
      if (bpm !== undefined) setBpm(bpm);
      if (hrv_sdnn !== undefined) setHrvSdnn(hrv_sdnn);
      if (hrv_rmssd !== undefined) setHrvRmssd(hrv_rmssd);
      if (confidence !== undefined) setConfidence(confidence);
      if (afib_suspected !== undefined) setAfibSuspected(afib_suspected);
      if (afib_score !== undefined) setAfibScore(afib_score);
      if (tachycardia_suspected !== undefined) setTachycardiaSuspected(tachycardia_suspected);

      if (is_new_beat) {
        setTotalBeats(prev => prev + 1);
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

      // chunk2 chỉ có khi bản ghi PhysioNet có kênh thứ 2 (vd MLII + V1/V5) - xem data_streamer.py.
      // Không dùng cho AI, chỉ hiển thị thêm 1 dải sóng tham chiếu như máy Holter 2 kênh thật.
      if (chunk2) {
        const rawY2 = [...yData2Ref.current, ...chunk2];
        yData2Ref.current = rawY2.length > MAX_POINTS ? rawY2.slice(rawY2.length - MAX_POINTS) : rawY2;
      }

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

      const base = `${resolveWsBase(settings.wsUrl)}/ws/ecg`;
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
        yData2Ref.current = [];
        setXData([]);
        setYData([]);
        setYData2([]);
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
  }, [selectedRecord, selectedPatient, settings.wsUrl, isAuthenticated]); // Chạy lại hiệu ứng khi bản ghi, bệnh nhân, wsUrl hoặc trạng thái đăng nhập thay đổi

  const value = {
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
    confidenceThreshold: settings.confidenceThreshold,
  };

  return (
    <MonitoringContext.Provider value={value}>
      {children}
    </MonitoringContext.Provider>
  );
};

export default MonitoringContext;
