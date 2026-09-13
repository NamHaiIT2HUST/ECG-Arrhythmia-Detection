from __future__ import annotations

from pathlib import Path

import numpy as np
import wfdb

from backend.core.hrv import compute_bpm, compute_rmssd, rr_to_ms
from backend.core.qrs_detector import pan_tompkins_r_peaks
from backend.core.signal_processing import bandpass_filter, notch_filter

DEFAULT_THRESHOLDS = {
    "rr_irregularity_threshold": 0.38,
    "bpm_threshold": 100,
    "positive_threshold": 0.72,
    "indeterminate_threshold": 0.5,
}


def _rr_irregularity(rr_ms: np.ndarray) -> float:
    """Tính độ không đều của chuỗi RR theo thang [0,1].

    Dùng một giá trị gộp dựa trên hệ số biến thiên (CV) và độ chênh lệch tuyệt đối
    trung bình giữa RR liên tiếp. Mục tiêu là nén nhiều đặc trưng HRV thành một chỉ số
    đơn giản để sàng lọc AFib.
    """
    rr_ms = np.asarray(rr_ms, dtype=np.float64)
    if rr_ms.size < 2:
        return 0.0
    mean_rr = float(np.mean(rr_ms))
    if mean_rr <= 0:
        return 0.0
    cv = float(np.std(rr_ms, ddof=1) / mean_rr) if rr_ms.size > 1 else 0.0
    diff_ratio = float(np.mean(np.abs(np.diff(rr_ms))) / mean_rr)
    return float(np.clip(0.7 * cv + 0.3 * diff_ratio, 0.0, 1.0))


def _estimate_p_wave_presence(signal: np.ndarray, r_peaks: np.ndarray, fs: float) -> float:
    """Ước lượng xem có P-wave rõ hay không dựa trên biên độ ở vùng PR trước QRS.

    Đây không phải phép đo bệnh lý chuẩn, nhưng đủ để làm feature sàng lọc nhanh và
    không phụ thuộc vào mô hình training. Giả sử nếu vùng PR trước QRS có biên độ thấp,
    khả năng thiếu P-wave cao.
    """
    if r_peaks.size == 0:
        return 0.0

    scores = []
    max_count = min(len(r_peaks), 20)
    for r_peak in r_peaks[:max_count]:
        pr_start = max(0, int(r_peak - 0.22 * fs))
        pr_end = max(0, int(r_peak - 0.08 * fs))
        if pr_end <= pr_start:
            continue
        segment = signal[pr_start:pr_end]
        if segment.size == 0:
            continue
        baseline = float(np.median(segment))
        amplitude = float(np.max(np.abs(segment - baseline)))
        scores.append(1.0 if amplitude >= 0.03 else 0.0)

    if not scores:
        return 0.0
    return float(np.mean(scores))


def _compute_rr_metrics(signal: np.ndarray, fs: float) -> dict:
    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    r_peaks = pan_tompkins_r_peaks(clean, fs=fs)
    rr_samples = np.diff(r_peaks) if r_peaks.size > 1 else np.array([], dtype=np.int64)
    rr_ms = np.asarray([rr_to_ms(rr, fs) for rr in rr_samples], dtype=np.float64)

    if rr_ms.size == 0:
        return {
            "r_peaks": r_peaks,
            "rr_ms": rr_ms,
            "bpm": 0.0,
            "rr_irregularity": 0.0,
            "rr_rmssd_ms": 0.0,
            "p_wave_present": 0.0,
        }

    bpm_values = [compute_bpm(rr, fs) for rr in rr_samples]
    mean_bpm = float(np.mean(bpm_values)) if bpm_values else 0.0
    rr_irregularity = _rr_irregularity(rr_ms)
    rr_rmssd_ms = float(compute_rmssd(rr_ms))
    p_wave_present = _estimate_p_wave_presence(clean, r_peaks, fs)

    return {
        "r_peaks": r_peaks,
        "rr_ms": rr_ms,
        "bpm": mean_bpm,
        "rr_irregularity": rr_irregularity,
        "rr_rmssd_ms": rr_rmssd_ms,
        "p_wave_present": p_wave_present,
    }


def calibrate_thresholds_from_afdb(afdb_dir: str | Path | None = None) -> dict:
    """Hiệu chỉnh ngưỡng theo các record AFDB mẫu nếu có sẵn trong data/raw/afdb.

    Mục tiêu:
    - không bắt buộc phải có dữ liệu AFDB mới trong máy dev
    - nếu AFDB đã được tải, dùng nó để tinh chỉnh ngưỡng không đều RR và ngưỡng AFib
    - nếu chưa có, fallback về giá trị mặc định đã chọn từ phân tích thực nghiệm.
    """
    thresholds = DEFAULT_THRESHOLDS.copy()
    afdb_dir = Path(afdb_dir) if afdb_dir is not None else Path("data/raw/afdb")
    if not afdb_dir.exists():
        return thresholds

    record_files = sorted(afdb_dir.glob("*.dat"))
    if not record_files:
        return thresholds

    irregularity_values = []
    bpm_values = []

    for dat_file in record_files[:8]:
        try:
            base_path = dat_file.with_suffix("")
            signal, fields = wfdb.rdsamp(str(base_path), channels=[0], return_res=False)
        except Exception:
            try:
                record = wfdb.rdrecord(str(base_path), channels=[0], return_res=False)
                signal = record.p_signal[:, 0]
            except Exception:
                continue

        if signal is None or np.asarray(signal).size < 360:
            continue

        sig = np.asarray(signal).reshape(-1)
        metrics = _compute_rr_metrics(sig, fs=float(fields.get("fs", 360))) if isinstance(fields, dict) else _compute_rr_metrics(sig, fs=360.0)
        if metrics["rr_ms"].size > 0:
            irregularity_values.append(metrics["rr_irregularity"])
            bpm_values.append(metrics["bpm"])

    if irregularity_values:
        median_irregularity = float(np.median(irregularity_values))
        thresholds["rr_irregularity_threshold"] = float(np.clip(median_irregularity * 0.9, 0.25, 0.7))
        thresholds["positive_threshold"] = float(np.clip(thresholds["rr_irregularity_threshold"] + 0.2, 0.55, 0.85))
        thresholds["indeterminate_threshold"] = float(np.clip(thresholds["rr_irregularity_threshold"] * 0.9, 0.4, 0.7))

    if bpm_values:
        median_bpm = float(np.median(bpm_values))
        thresholds["bpm_threshold"] = int(np.clip(round(median_bpm * 0.9), 90, 140))

    return thresholds


def screen_afib_signal(signal: np.ndarray, fs: float = 360.0) -> dict:
    """Chạy screening rung nhĩ theo logic rule-based + calibration ngưỡng AFDB.

    Trả về dict gồm:
    - status: negative | indeterminate | positive
    - confidence: độ tin cậy [0,1]
    - bpm
    - rr_irregularity
    - rr_rmssd_ms
    - thresholds_used
    - recommendation
    """
    signal = np.asarray(signal, dtype=np.float64)
    if signal.size < int(fs * 2):
        return {
            "status": "indeterminate",
            "confidence": 0.0,
            "bpm": 0.0,
            "rr_irregularity": 0.0,
            "rr_rmssd_ms": 0.0,
            "thresholds_used": DEFAULT_THRESHOLDS,
            "recommendation": "Dữ liệu quá ngắn để sàng lọc rung nhĩ. Cần ít nhất 2 giây ECG có chất lượng đủ.",
        }

    thresholds = calibrate_thresholds_from_afdb()
    metrics = _compute_rr_metrics(signal, fs=fs)
    rr_irregularity = float(metrics["rr_irregularity"])
    rr_rmssd_ms = float(metrics["rr_rmssd_ms"])
    bpm = float(metrics["bpm"])
    p_wave_present = float(metrics["p_wave_present"])
    absence_p_wave = 1.0 - p_wave_present

    hr_score = min(1.0, max(0.0, (bpm - 80.0) / 80.0)) if bpm > 0 else 0.0
    irregularity_score = min(1.0, rr_irregularity / max(thresholds["rr_irregularity_threshold"], 1e-6)) if rr_irregularity > 0 else 0.0
    p_wave_score = absence_p_wave

    raw_score = 0.45 * irregularity_score + 0.25 * hr_score + 0.30 * p_wave_score
    if rr_irregularity <= 0 and bpm <= 0:
        status = "indeterminate"
        confidence = 0.12
    elif (raw_score >= thresholds["positive_threshold"] and (rr_irregularity >= thresholds["rr_irregularity_threshold"] or bpm >= thresholds["bpm_threshold"])):
        status = "positive"
        confidence = float(np.clip(raw_score, 0.55, 0.99))
    elif raw_score >= thresholds["indeterminate_threshold"]:
        status = "indeterminate"
        confidence = float(np.clip(raw_score, 0.4, 0.8))
    else:
        status = "negative"
        confidence = float(np.clip(1.0 - raw_score, 0.5, 0.96))

    if status == "positive":
        recommendation = "Khả năng cao có rung nhĩ. Khuyến nghị kiểm tra lại bằng ECG 12 lead hoặc bác sĩ chuyên khoa."
    elif status == "indeterminate":
        recommendation = "Kết quả chưa chắc chắn; cần đoạn ECG dài hơn hoặc kiểm tra bổ sung để loại trừ rung nhĩ."
    else:
        recommendation = "Không thấy dấu hiệu sàng lọc rung nhĩ trong đoạn ECG hiện tại."

    return {
        "status": status,
        "confidence": round(float(confidence), 3),
        "bpm": round(float(bpm), 1),
        "rr_irregularity": round(float(rr_irregularity), 3),
        "rr_rmssd_ms": round(float(rr_rmssd_ms), 2),
        "p_wave_present": round(float(p_wave_present), 3),
        "sample_count": int(metrics["r_peaks"].size),
        "thresholds_used": thresholds,
        "recommendation": recommendation,
    }
