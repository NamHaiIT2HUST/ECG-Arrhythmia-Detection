/**
 * alarmAudio.js — Web Audio API alarm engine
 * Không cần file mp3 — tự tổng hợp beep bằng OscillatorNode
 * Tham chiếu: IEC 60601-1-8 (chuẩn âm thanh cảnh báo y tế)
 *
 * Mức 2: 1 beep/giây (chú ý)
 * Mức 3: cụm 3 beep liên tiếp mỗi 2 giây (khẩn cấp)
 */

let audioCtx = null;
let alarmInterval = null;
let currentLevel = 0;
let globallyMuted = false;

const getAudioContext = () => {
  if (!audioCtx || audioCtx.state === 'closed') {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  // Resume nếu bị suspend (browser policy: cần user gesture lần đầu)
  if (audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
};

/**
 * Phát 1 beep đơn
 * @param {number} frequency - Hz
 * @param {number} duration - giây
 * @param {number} startTime - audioCtx.currentTime offset
 */
const scheduleBeep = (frequency, duration, startTime) => {
  const ctx = getAudioContext();
  const oscillator = ctx.createOscillator();
  const gainNode = ctx.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(ctx.destination);

  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(frequency, startTime);

  // Envelope: fade in 10ms, sustain, fade out 30ms (tránh click artifact)
  gainNode.gain.setValueAtTime(0, startTime);
  gainNode.gain.linearRampToValueAtTime(0.4, startTime + 0.01);
  gainNode.gain.setValueAtTime(0.4, startTime + duration - 0.03);
  gainNode.gain.linearRampToValueAtTime(0, startTime + duration);

  oscillator.start(startTime);
  oscillator.stop(startTime + duration);
};

/**
 * Phát 1 nhịp cảnh báo theo mức
 */
const playAlarmPattern = (level) => {
  const ctx = getAudioContext();
  const now = ctx.currentTime;

  if (level === 2) {
    // Mức 2: 1 beep 880Hz, 150ms
    scheduleBeep(880, 0.15, now);
  } else if (level === 3) {
    // Mức 3: cụm 3 beep 1320Hz, 100ms mỗi cái, cách nhau 150ms
    scheduleBeep(1320, 0.1, now);
    scheduleBeep(1320, 0.1, now + 0.15);
    scheduleBeep(1320, 0.1, now + 0.30);
  }
};

/**
 * Bắt đầu cảnh báo liên tục
 * @param {number} level - 2 hoặc 3
 */
export const startAlarm = (level) => {
  if (globallyMuted) return;
  if (level < 2) return; // Mức 1 không cần âm thanh
  if (currentLevel === level && alarmInterval) return; // Đã đang chạy đúng mức

  stopAlarm();
  currentLevel = level;

  const intervalMs = level === 2 ? 1000 : 2000; // Mức 2: 1s, Mức 3: 2s

  playAlarmPattern(level); // Phát ngay lập tức
  alarmInterval = setInterval(() => playAlarmPattern(level), intervalMs);
};

/**
 * Dừng tất cả cảnh báo âm thanh
 */
export const stopAlarm = () => {
  if (alarmInterval) {
    clearInterval(alarmInterval);
    alarmInterval = null;
  }
  currentLevel = 0;
};

export const setMuted = (v) => {
  globallyMuted = !!v;
  if (globallyMuted) stopAlarm();
};
