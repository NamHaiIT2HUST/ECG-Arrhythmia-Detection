import React, { useState, useEffect } from 'react';
import StatCards from '../components/dashboard/StatCards';
import ECGChart from '../components/dashboard/ECGChart';
import LoadingSpinner from '../components/dashboard/LoadingSpinner';

const MAX_POINTS = 1000;

const DashboardPage = () => {
  const [connectionStatus, setConnectionStatus] = useState('Đang kết nối...');
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  
  const [xData, setXData] = useState([]);
  const [yData, setYData] = useState([]);
  const [currentHeatmap, setCurrentHeatmap] = useState(null);
  
  const [latestPrediction, setLatestPrediction] = useState('Đang tải...');
  const [latency, setLatency] = useState(0);

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
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      {isInitialLoading ? (
        <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LoadingSpinner />
        </div>
      ) : (
        <>
          <StatCards latestPrediction={latestPrediction} latency={latency} />
          <div style={{ display: 'flex', flex: 1, minHeight: '0' }}>
            <ECGChart xData={xData} yData={yData} heatmap={currentHeatmap} />
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardPage;