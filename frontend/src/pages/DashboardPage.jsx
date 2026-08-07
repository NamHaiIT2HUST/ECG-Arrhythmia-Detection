import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import StatCards from '../components/dashboard/StatCards';
import ECGChart from '../components/dashboard/ECGChart';
import PatientInfo from '../components/dashboard/PatientInfo';
import EventLog from '../components/dashboard/EventLog';
import LoadingSpinner from '../components/dashboard/LoadingSpinner';

const MAX_POINTS = 1000;

const DashboardPage = () => {
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  
  // Dùng state mảng cho luồng dữ liệu
  const [xData, setXData] = useState([]);
  const [yData, setYData] = useState([]);
  
  // Dữ liệu cho XAI
  const [currentHeatmap, setCurrentHeatmap] = useState(null);
  
  const [logs, setLogs] = useState([]);
  const [latestPrediction, setLatestPrediction] = useState('Đang tải...');
  const [latency, setLatency] = useState(0);
  
  const pointCounterRef = useRef(0);

  useEffect(() => {
    let ws = null;
    let reconnectTimeout = null;

    const handleNewData = (data) => {
      const { chunk, prediction, latency_ms, heatmap } = data;
      
      setLatency(latency_ms);
      setLatestPrediction(prediction);
      if(heatmap) setCurrentHeatmap(heatmap);
      
      setYData(prevY => {
        const newY = [...prevY, ...chunk];
        if (newY.length > MAX_POINTS) return newY.slice(newY.length - MAX_POINTS);
        return newY;
      });
      
      setXData(prevX => {
        const lastX = prevX.length > 0 ? prevX[prevX.length - 1] : 0;
        const newXChunks = Array.from({length: chunk.length}, (_, i) => lastX + i + 1);
        const newX = [...prevX, ...newXChunks];
        if (newX.length > MAX_POINTS) return newX.slice(newX.length - MAX_POINTS);
        return newX;
      });

      if (prediction && prediction.includes('CẢNH BÁO')) {
        setLogs(prevLogs => {
          // Tránh bị spam log quá nhiều lần cho cùng 1 cụm sóng
          const lastLog = prevLogs[0];
          if (lastLog && (Date.now() - lastLog.timestamp < 1000) && lastLog.prediction === prediction) {
            return prevLogs;
          }
          const newLog = {
            id: Date.now() + Math.random(),
            timestamp: Date.now(),
            time: new Date().toLocaleTimeString(),
            prediction: prediction,
            value: "Bất thường detected"
          };
          return [newLog, ...prevLogs].slice(0, 50);
        });
      }
    };

    const connect = () => {
      if (ws) {
        try { ws.close(); } catch (e) {}
      }

      ws = new WebSocket('ws://localhost:8000/ws/ecg');

      ws.onopen = () => {
        setConnectionStatus('Đã kết nối');
        setIsInitialLoading(false);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleNewData(data);
        } catch (err) {
          console.error('Lỗi giải mã JSON WebSocket:', err);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('Đang kết nối lại...');
        setIsInitialLoading(false);
        reconnectTimeout = setTimeout(connect, 3000);
      };

      ws.onerror = (err) => {
        console.error('Lỗi WebSocket:', err);
        ws.close();
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header connectionStatus={connectionStatus} latency={latency} />
        <main style={{ flex: 1, padding: '25px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '25px' }}>
          {isInitialLoading ? (
            <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <LoadingSpinner />
            </div>
          ) : (
            <>
              <StatCards latestPrediction={latestPrediction} connectionStatus={connectionStatus} latency={latency} />
              <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: '0' }}>
                <div style={{ flex: 7, display: 'flex' }}>
                  <ECGChart xData={xData} yData={yData} heatmap={currentHeatmap} />
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