import numpy as np

from backend.core.hrv import rr_to_ms


class AfibScreener:
    """Phân tích RR-interval để phát hiện dấu hiệu AFib theo nhịp điệu.

    Cách tiếp cận: tính độ không đều RR, pNN50, và mức độ dao động của chuỗi RR.
    Điểm AFib không phải là chẩn đoán tuyệt đối — đây là tầng sàng lọc nhanh, dùng
    để cảnh báo khi RR không đều "irregularly irregular" như rung nhĩ.
    """

    # threshold=0.62 vẫn là giá trị CHỌN TAY theo trực giác, CHƯA qua kiểm chứng thống
    # kê đáng tin — xem backend/scripts/calibrate_afib_thresholds.py (đã sửa đúng
    # phương pháp: đọc nhãn nhịp điệu thật từ AFDB thay vì giả định tất cả là AFib).
    # Đã thử chạy calibrate trên 1 đoạn ngắn (~10 phút, record AFDB 04015) do môi
    # trường tải dữ liệu quá chậm lúc thử (~7.6KB/s, không tải nổi bản ghi đầy đủ
    # ~27MB) — kết quả KHÔNG đủ tin cậy để đổi ngưỡng (Youden's J ~0, gần như ngẫu
    # nhiên), nhưng phát hiện điều đáng chú ý: các hằng số bão hoà công thức
    # (irregularity/0.25, pnn50/35, rmssd/120 bên dưới _compute_metrics) có thể đang
    # quá NHẠY — ở đúng bệnh nhân AFDB 04015 này, ngay cả đoạn nhịp "N" (không AFib)
    # cũng đã cho điểm 0.8-1.0 (bão hoà), gần bằng đoạn AFib thật. Cần chạy lại
    # calibrate_afib_thresholds.py với ĐẦY ĐỦ nhiều bản ghi AFDB (không bị cắt ngắn
    # vì mạng chậm) trước khi đổi threshold này dựa trên số liệu thật.
    def __init__(self, fs=360, max_history=50, threshold=0.62):
        self.fs = fs
        self.max_history = max_history
        self.threshold = threshold
        self._rr_ms_history = []
        self._last_r_peak = None

    def update(self, r_peak_sample: int | None) -> dict:
        """Cập nhật chuỗi RR theo chấm R mới, trả về kết quả AFib ở thời điểm hiện tại."""
        if r_peak_sample is not None and self._last_r_peak is not None:
            rr_samples = r_peak_sample - self._last_r_peak
            if rr_samples > 0:
                self._rr_ms_history.append(rr_to_ms(rr_samples, self.fs))
                if len(self._rr_ms_history) > self.max_history:
                    self._rr_ms_history.pop(0)
        self._last_r_peak = r_peak_sample

        metrics = self._compute_metrics()
        afib_score = metrics["afib_score"]
        return {
            "afib_suspected": bool(afib_score >= self.threshold),
            "afib_score": round(float(afib_score), 3),
            "rr_irregularity": round(float(metrics["rr_irregularity"]), 3),
            "rr_rmssd_ms": round(float(metrics["rr_rmssd_ms"]), 2),
            "pnn50": round(float(metrics["pnn50"]), 2),
            "threshold": self.threshold,
        }

    def _compute_metrics(self):
        rr = np.asarray(self._rr_ms_history, dtype=np.float64)
        if rr.size < 4:
            return {
                "afib_score": 0.0,
                "rr_irregularity": 0.0,
                "rr_rmssd_ms": 0.0,
                "pnn50": 0.0,
            }

        rr_mean = float(np.mean(rr))
        rr_std = float(np.std(rr, ddof=1)) if rr.size > 1 else 0.0
        rr_irregularity = rr_std / rr_mean if rr_mean > 0 else 0.0

        diffs = np.abs(np.diff(rr))
        pnn50 = float(np.mean(diffs > 50.0) * 100.0) if diffs.size else 0.0
        rmssd = float(np.sqrt(np.mean(np.square(diffs)))) if diffs.size else 0.0

        # Tỷ lệ biến thiên RR lớn và khoảng RR không đều đóng vai trò quan trọng trong AFib.
        irregularity_term = min(1.0, rr_irregularity / 0.25)
        pnn50_term = min(1.0, pnn50 / 35.0)
        rmssd_term = min(1.0, rmssd / 120.0)

        afib_score = 0.45 * irregularity_term + 0.35 * pnn50_term + 0.20 * rmssd_term
        return {
            "afib_score": float(np.clip(afib_score, 0.0, 1.0)),
            "rr_irregularity": float(rr_irregularity),
            "rr_rmssd_ms": float(rmssd),
            "pnn50": float(pnn50),
        }
