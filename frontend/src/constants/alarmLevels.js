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

/**
 * Mức cảnh báo cho các điều kiện KHÔNG phải nhãn AAMI từng nhịp (afib_suspected/
 * tachycardia_suspected từ payload WS) — dùng chung nguồn duy nhất này với ALARM_LEVELS,
 * cùng cơ chế sound/push, để AlarmContext.triggerAlarm xử lý đồng nhất cả 2 loại điều kiện.
 * Giữ đúng mức độ đã dùng cho màu badge ở StatCards.jsx (AFib đỏ/mức 3, tachycardia vàng/mức 2).
 */
export const EXTRA_CONDITIONS = {
  afib: {
    level: 3,
    label: '🚨 Khẩn cấp — Nghi ngờ Rung Nhĩ (AFib)',
    sound: true,
    push: true,
  },
  tachycardia: {
    level: 2,
    label: 'Chú ý — Nhịp Tim Nhanh Bất Thường (≥100 bpm)',
    sound: false,
    push: false,
  },
};
