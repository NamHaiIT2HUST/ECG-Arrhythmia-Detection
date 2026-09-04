/**
 * Bảng ánh xạ nhãn AAMI → mức độ cảnh báo (nguồn DUY NHẤT — không định nghĩa lại ở chỗ khác)
 * Mức 1: Bình thường
 * Mức 2: Chú ý (vàng) — hiển thị màu, không âm thanh
 * Mức 3: Khẩn cấp (đỏ) — âm thanh + push notification
 */
export const ALARM_LEVELS = {
  'BÌNH THƯỜNG': {
    level: 1,
    color: 'green',
    colorHex: '#10b981',
    bgHex: '#ecfdf5',
    label: 'Bình thường',
    sound: false,
    push: false,
    icon: '🟢',
  },
  'CẢNH BÁO: TRÊN THẤT (S)': {
    level: 2,
    color: 'yellow',
    colorHex: '#f59e0b',
    bgHex: '#fffbeb',
    label: 'Chú ý — Trên thất (SVPB)',
    sound: false,
    push: false,
    icon: '🟡',
  },
  'CẢNH BÁO: CHƯA RÕ (Q)': {
    level: 2,
    color: 'yellow',
    colorHex: '#f59e0b',
    bgHex: '#fffbeb',
    label: 'Chú ý — Chưa phân loại (Q)',
    sound: false,
    push: false,
    icon: '🟡',
  },
  'CẢNH BÁO: NHỊP THẤT (V)': {
    level: 3,
    color: 'red',
    colorHex: '#ef4444',
    bgHex: '#fef2f2',
    label: '🚨 Khẩn cấp — Ngoại tâm thu thất (PVC)',
    sound: true,
    push: true,
    icon: '🔴',
  },
  'CẢNH BÁO: HỢP NHẤT (F)': {
    level: 3,
    color: 'red',
    colorHex: '#ef4444',
    bgHex: '#fef2f2',
    label: '🚨 Khẩn cấp — Nhịp hợp nhất (Fusion)',
    sound: true,
    push: true,
    icon: '🔴',
  },
};

/**
 * Lấy thông tin mức cảnh báo từ nhãn AAMI.
 * @param {string} prediction — nhãn từ WS payload
 * @returns {object} alarm level info, hoặc level 1 (bình thường) nếu không nhận ra
 */
export const getAlarmLevel = (prediction) => {
  if (!prediction) return ALARM_LEVELS['BÌNH THƯỜNG'];
  return ALARM_LEVELS[prediction] ?? ALARM_LEVELS['BÌNH THƯỜNG'];
};
