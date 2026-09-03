import React, { createContext, useState, useContext, useRef, useCallback, useEffect } from 'react';
import { getAlarmLevel } from '../constants/alarmLevels';
import { startAlarm, stopAlarm } from '../utils/alarmAudio';

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
  }, []);

  /**
   * Gọi khi nhận prediction mới từ WS.
   * @param {string} prediction - nhãn AAMI
   * @param {number} confidenceThreshold - ngưỡng confidence (0-1), mặc định 0
   * @param {number} confidence - confidence thực tế từ WS
   */
  const triggerAlarm = useCallback((prediction, confidenceThreshold = 0, confidence = 1) => {
    const alarm = getAlarmLevel(prediction);

    // Nếu confidence dưới ngưỡng → không kích hoạt (Settings CP4.5)
    if (alarm.level > 1 && confidence < confidenceThreshold) {
      setCurrentAlarmLevel(0);
      stopAlarm();
      return;
    }

    setCurrentAlarmLevel(alarm.level);

    if (alarm.level < 2) {
      stopAlarm();
      return;
    }

    if (!isMuted && alarm.sound) {
      startAlarm(alarm.level);
    }

    // Push Notification (chỉ mức 3)
    if (alarm.push && alarm.level === 3 && !isMuted) {
      if (Notification.permission === 'granted') {
        try {
          new Notification('⚠️ CẢNH BÁO ECG KHẨN CẤP', {
            body: `Phát hiện: ${prediction}\nYêu cầu kiểm tra ngay bệnh nhân!`,
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
