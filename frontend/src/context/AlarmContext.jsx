import React, { createContext, useState, useContext, useRef, useCallback, useEffect } from 'react';
import { ALARM_LEVELS, getAlarmLevel, EXTRA_CONDITIONS } from '../constants/alarmLevels';
import { startAlarm, stopAlarm, setMuted } from '../utils/alarmAudio';

const AlarmContext = createContext();

export const useAlarm = () => useContext(AlarmContext);

const MUTE_DURATION_MS = 2 * 60 * 1000; // 2 phút — chuẩn y tế, không cho tắt vĩnh viễn

export const AlarmProvider = ({ children }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [snoozeCountdown, setSnoozeCountdown] = useState(0); // giây còn lại
  const [currentAlarmLevel, setCurrentAlarmLevel] = useState(0);
  const muteTimerRef = useRef(null);
  const countdownTimerRef = useRef(null);

  const clearMuteTimers = () => {
    if (muteTimerRef.current) clearTimeout(muteTimerRef.current);
    if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
  };

  /**
   * Tắt âm thanh 2 phút rồi tự bật lại
   */
  const muteAlarm = useCallback(() => {
    clearMuteTimers();
    setIsMuted(true);
    setMuted(true);
    stopAlarm();
    let remaining = Math.floor(MUTE_DURATION_MS / 1000);
    setSnoozeCountdown(remaining);

    countdownTimerRef.current = setInterval(() => {
      remaining -= 1;
      setSnoozeCountdown(remaining);
      if (remaining <= 0) clearInterval(countdownTimerRef.current);
    }, 1000);

    muteTimerRef.current = setTimeout(() => {
      setIsMuted(false);
      setSnoozeCountdown(0);
    }, MUTE_DURATION_MS);
  }, []);

  const unmuteAlarm = useCallback(() => {
    clearMuteTimers();
    setIsMuted(false);
    setSnoozeCountdown(0);
    setMuted(false);
  }, []);

  /**
   * Gọi khi nhận prediction mới từ WS (mỗi khi có 1 nhịp mới được chẩn đoán, kể cả nhịp
   * Bình thường - cần gọi liên tục để tự tắt cảnh báo cũ đúng lúc, không chỉ lúc bất thường).
   * @param {string} prediction - nhãn AAMI
   * @param {number} confidenceThreshold - ngưỡng confidence (0-1), mặc định 0
   * @param {number} confidence - confidence thực tế từ WS
   * @param {{afibSuspected?: boolean, tachycardiaSuspected?: boolean}} extras - các điều kiện
   *   cảnh báo KHÔNG dựa trên nhãn AAMI từng nhịp (rung nhĩ/nhịp nhanh theo nhịp điệu nhiều
   *   nhịp) - có thể đang true dù prediction của đúng nhịp này là Bình thường.
   */
  const triggerAlarm = useCallback((prediction, confidenceThreshold = 0, confidence = 1, extras = {}) => {
    const aami = getAlarmLevel(prediction);
    // Nếu confidence dưới ngưỡng → coi như AAMI không kích hoạt (Settings CP4.5), nhưng
    // AFib/tachycardia không phụ thuộc confidence của model phân loại nhịp nên vẫn xét riêng.
    const aamiActive = !(aami.level > 1 && confidence < confidenceThreshold);
    const candidates = [aamiActive ? aami : ALARM_LEVELS['BÌNH THƯỜNG']];
    if (extras.afibSuspected) candidates.push(EXTRA_CONDITIONS.afib);
    if (extras.tachycardiaSuspected) candidates.push(EXTRA_CONDITIONS.tachycardia);

    // Điều kiện nào mức độ cao nhất thắng, quyết định âm thanh/push/label hiển thị.
    const winner = candidates.reduce((max, c) => (c.level > max.level ? c : max));

    setCurrentAlarmLevel(winner.level);

    if (winner.level < 2) {
      stopAlarm();
      return;
    }

    if (!isMuted && winner.sound) {
      startAlarm(winner.level);
    }

    // Push Notification (chỉ mức 3)
    if (winner.push && winner.level === 3 && !isMuted) {
      if (Notification.permission === 'granted') {
        try {
          new Notification('⚠️ CẢNH BÁO ECG KHẨN CẤP', {
            body: `Phát hiện: ${winner.label}\nYêu cầu kiểm tra ngay bệnh nhân!`,
            icon: '/favicon.ico',
            tag: 'ecg-alarm', // tag để không spam nhiều notification cùng lúc
          });
        } catch (e) {
          console.warn('Không thể gửi notification:', e);
        }
      }
    }
  }, [isMuted]);

  // Dừng âm thanh khi mute state thay đổi
  useEffect(() => {
    if (isMuted) stopAlarm();
  }, [isMuted]);

  // Cleanup khi unmount
  useEffect(() => () => {
    clearMuteTimers();
    stopAlarm();
  }, []);

  return (
    <AlarmContext.Provider value={{
      isMuted,
      snoozeCountdown,
      currentAlarmLevel,
      muteAlarm,
      unmuteAlarm,
      triggerAlarm,
    }}>
      {children}
    </AlarmContext.Provider>
  );
};
