import React from 'react';
import { getAlarmLevel, getAamiCode } from '../../constants/alarmLevels';

const StatCards = ({ latestPrediction, latency, latencyE2e, bpm, hrv_sdnn, hrv_rmssd, confidence, afibSuspected, afibScore, tachycardiaSuspected }) => {
  const isDanger = getAlarmLevel(latestPrediction).level === 3 || Boolean(afibSuspected) || Boolean(tachycardiaSuspected);
  // Ngưỡng KPI cốt lõi của dự án: tổng độ trễ hệ thống (End-to-End) phải dưới 2 giây - xem
  // Project Definition mục "Đánh giá toàn diện hệ thống".
  const isLatencyOverBudget = latencyE2e > 2000;

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '15px' }}>
      
      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        backgroundColor: isDanger ? 'var(--danger-bg)' : 'var(--card-bg)',
        borderLeft: isDanger ? '4px solid var(--danger)' : '4px solid var(--primary)',
        gridColumn: 'span 2'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: isDanger ? 'var(--danger)' : 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🤖 Phân Tích AI
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <p style={{
            margin: 0,
            fontSize: '22px',
            fontWeight: '700',
            color: isDanger ? 'var(--danger)' : 'var(--text-main)'
          }}>
            {latestPrediction}
          </p>
          <span style={{
            fontSize: '12px', fontWeight: '700', fontFamily: 'monospace',
            color: isDanger ? 'var(--danger)' : 'var(--text-muted)',
            border: `1px solid ${isDanger ? 'var(--danger)' : 'var(--border-color)'}`,
            borderRadius: '4px', padding: '1px 6px',
          }}>
            {getAamiCode(latestPrediction)}
          </span>
        </div>
        {Boolean(afibSuspected) && (
          <div style={{ marginTop: '4px', fontSize: '12px', fontWeight: '700', color: 'var(--danger)', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '999px', padding: '4px 8px', display: 'inline-flex', alignItems: 'center', gap: '4px', width: 'fit-content' }}>
            ⚠️ Nghi ngờ Rung Nhĩ (score {Number(afibScore ?? 0).toFixed(2)})
          </div>
        )}
        {Boolean(tachycardiaSuspected) && (
          <div style={{ marginTop: '4px', fontSize: '12px', fontWeight: '700', color: '#f59e0b', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '999px', padding: '4px 8px', display: 'inline-flex', alignItems: 'center', gap: '4px', width: 'fit-content' }}>
            ⚡ Nhịp Tim Nhanh Bất Thường (≥100 bpm)
          </div>
        )}
      </div>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #22c55e'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          💓 Nhịp tim (BPM)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {bpm ?? '--'}
          </p>
        </div>
        {/* RR interval = 60000/BPM - suy ra trực tiếp từ BPM đã đo, không phải số liệu mới */}
        <p style={{ margin: 0, fontSize: '11.5px', color: 'var(--text-muted)' }}>
          RR: {bpm ? `${Math.round(60000 / bpm)} ms` : '--'}
        </p>
      </div>

      <div className="card" style={{ 
        padding: '15px 20px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #06b6d4'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          📈 HRV (SDNN)
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {hrv_sdnn != null ? hrv_sdnn.toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>ms</span>
        </div>
        <p style={{ margin: 0, fontSize: '11.5px', color: 'var(--text-muted)' }}>
          RMSSD: {hrv_rmssd != null ? `${hrv_rmssd.toFixed(1)} ms` : '--'}
        </p>
      </div>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        borderLeft: '4px solid #f59e0b'
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          🎯 Độ tin cậy AI
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: 'var(--text-main)' }}>
            {confidence != null ? (confidence * 100).toFixed(1) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>%</span>
        </div>
      </div>

      <div className="card" style={{
        padding: '15px 20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '8px',
        borderLeft: `4px solid ${isLatencyOverBudget ? 'var(--danger)' : 'var(--success)'}`
      }}>
        <h3 style={{ margin: 0, fontSize: '13px', color: 'var(--text-muted)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '1px' }}>
          ⏱️ Độ trễ xử lý
        </h3>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '5px' }}>
          <p style={{ margin: 0, fontSize: '22px', fontWeight: '700', color: isLatencyOverBudget ? 'var(--danger)' : 'var(--text-main)' }}>
            {latencyE2e ? latencyE2e.toFixed(0) : '--'}
          </p>
          <span style={{ fontSize: '14px', color: 'var(--text-muted)', fontWeight: '500' }}>ms (E2E)</span>
        </div>
        <p style={{ margin: 0, fontSize: '11.5px', color: 'var(--text-muted)' }}>
          AI: {latency ? `${latency.toFixed(1)} ms` : '--'} · mục tiêu &lt;2000ms
        </p>
      </div>

    </div>
  );
};

export default StatCards;
