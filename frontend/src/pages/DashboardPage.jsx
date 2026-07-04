import React, { useState, useEffect } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import StatCards from '../components/dashboard/StatCards';
import ECGChart from '../components/dashboard/ECGChart';
import PatientInfo from '../components/dashboard/PatientInfo';
import EventLog from '../components/dashboard/EventLog';
import LoadingSpinner from '../components/dashboard/LoadingSpinner';

const DashboardPage = () => {
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [xData, setXData] = useState([]);
  const [yData, setYData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [logs, setLogs] = useState([]);
  const [latestPrediction, setLatestPrediction] = useState('Đang tải...');
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    let ws = null;
    let fallbackInterval = null;
    let reconnectTimeout = null;
    let pointIndex = 0;
    let hasConnectedOnce = false;

    const startFallback = () => {
      if (fallbackInterval) return;
      console.log("Khởi động dữ liệu mô phỏng do mất kết nối WebSocket.");
      fallbackInterval = setInterval(() => {
        // Tạo nhịp tim giả lập
        const isHeartbeat = pointIndex % 40 === 10 || pointIndex % 40 === 11 || pointIndex % 40 === 12;
        let value = 0;
        if (isHeartbeat) {
          if (pointIndex % 40 === 10) value = 0.5;
          else if (pointIndex % 40 === 11) value = 1.8; // Đỉnh R
          else if (pointIndex % 40 === 12) value = -0.4;
        } else {
          // Nhiễu nhẹ
          value = Math.random() * 0.1 - 0.05;
        }

        // Thi thoảng tạo PVC giả lập
        const isPVC = Math.random() > 0.98;
        if (isPVC && isHeartbeat) {
          value = Math.random() * 3.0 + 1.5; // Đỉnh PVC cao hơn bình thường
        }

        const prediction = isPVC ? "CẢNH BÁO PVC" : "BÌNH THƯỜNG";
        const mockLatency = Math.floor(Math.random() * 8) + 6;

        setLatency(mockLatency);
        setLatestPrediction(prediction);

        setXData(prevX => {
          const nextX = prevX.length > 0 ? prevX[prevX.length - 1] + 1 : 0;
          return [...prevX, nextX].slice(-150);
        });

        setYData(prevY => {
          return [...prevY, value].slice(-150);
        });

        setPredictions(prevPred => {
          return [...prevPred, prediction].slice(-150);
        });

        if (prediction === "CẢNH BÁO PVC") {
          setLogs(prevLogs => {
            const newLog = {
              id: Date.now() + Math.random(),
              time: new Date().toLocaleTimeString(),
              prediction: "CẢNH BÁO PVC (Phát hiện ngoại tâm thu thất)",
              value: value.toFixed(4)
            };
            return [newLog, ...prevLogs].slice(0, 50);
          });
        }

        pointIndex++;
      }, 100);
    };

    const connect = () => {
      if (ws) {
        try {
          ws.close();
        } catch (e) {}
      }

      ws = new WebSocket('ws://localhost:8000/ws/ecg');

      ws.onopen = () => {
        setConnectionStatus('Đã kết nối');
        setIsInitialLoading(false);
        hasConnectedOnce = true;
        if (fallbackInterval) {
          clearInterval(fallbackInterval);
          fallbackInterval = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const val = data.value;
          const pred = data.prediction;
          const lat = data.latency_ms;

          setLatency(lat);
          setLatestPrediction(pred);

          setXData(prevX => {
            const nextX = prevX.length > 0 ? prevX[prevX.length - 1] + 1 : 0;
            return [...prevX, nextX].slice(-150);
          });

          setYData(prevY => {
            return [...prevY, val].slice(-150);
          });

          setPredictions(prevPred => {
            return [...prevPred, pred].slice(-150);
          });

          if (pred && pred.includes('CẢNH BÁO')) {
            setLogs(prevLogs => {
              const newLog = {
                id: Date.now() + Math.random(),
                time: new Date().toLocaleTimeString(),
                prediction: pred,
                value: val.toFixed(4)
              };
              return [newLog, ...prevLogs].slice(0, 50);
            });
          }
        } catch (err) {
          console.error('Lỗi giải mã JSON WebSocket:', err);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('Đang kết nối lại...');
        // Nếu đã từng kết nối thành công, dùng dữ liệu mô phỏng để tránh màn hình trống hoặc các chỉ số bị reset về 0
        if (hasConnectedOnce) {
          startFallback();
        }
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error('Lỗi WebSocket, đóng để thực hiện tự động kết nối lại:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (fallbackInterval) clearInterval(fallbackInterval);
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-color)' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header connectionStatus={connectionStatus} latency={latency} />
        <main style={{ flex: 1, padding: '25px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '25px' }}>
          {isInitialLoading ? (
            <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ffffff' }}>
              <LoadingSpinner />
            </div>
          ) : (
            <>
              <StatCards latestPrediction={latestPrediction} connectionStatus={connectionStatus} latency={latency} />
              <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: '0' }}>
                <div style={{ flex: 7, display: 'flex' }}>
                  <ECGChart xData={xData} yData={yData} predictions={predictions} />
                </div>
                <div style={{ flex: 3, display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <PatientInfo />
                  <EventLog logs={logs} />
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;