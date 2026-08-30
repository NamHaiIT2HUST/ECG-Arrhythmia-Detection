import numpy as np

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import compute_all_beats
from backend.core.hrv import compute_bpm, compute_sdnn, compute_rmssd, rr_to_ms
from backend.service.inference_service import ai_service

MAX_ANOMALIES_IN_REPORT = 500
NORMAL_LABEL = 'BÌNH THƯỜNG'


def parse_ecg_csv(content: bytes) -> np.ndarray:
    """Đọc file CSV 1 cột giá trị biên độ tín hiệu ECG (có thể có hoặc không có dòng
    header, phân cách bằng dấu phẩy hoặc chấm phẩy). Nếu có nhiều cột (vd timestamp,value
    như `backend/scripts/generate_mock.py` sinh ra), lấy CỘT CUỐI làm giá trị tín hiệu.
    Dòng nào không đọc được thành số (vd dòng header) sẽ tự động bị bỏ qua.
    """
    text = content.decode('utf-8-sig', errors='ignore')
    values = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.replace(';', ',').split(',')
        candidate = parts[-1].strip()
        try:
            values.append(float(candidate))
        except ValueError:
            continue
    return np.array(values, dtype=np.float64)


def run_offline_diagnosis(signal, fs=360, max_anomalies=MAX_ANOMALIES_IN_REPORT):
    """Chạy chẩn đoán offline trên TOÀN BỘ tín hiệu đã tải lên: lọc nhiễu, phát hiện
    đỉnh R, cắt từng nhịp, chạy AI cho từng nhịp, rồi tổng hợp thành 1 báo cáo.

    Không trả về heatmap Grad-CAM cho từng nhịp bất thường (có thể lên tới hàng trăm/
    nghìn nhịp với 1 bản ghi dài) để báo cáo không phình quá lớn — muốn xem chi tiết
    XAI của 1 nhịp cụ thể thì dùng luồng real-time (`/ws/ecg`) + trang XAI hiện có.
    """
    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    beats = compute_all_beats(clean, fs=fs)

    class_counts = {}
    bpm_values = []
    rr_ms_history = []
    anomalies = []
    prev_r_peak = None

    for i, (r_peak_idx, window) in enumerate(beats):
        prediction, _heatmap, _latency, confidence = ai_service.predict(window)
        class_counts[prediction] = class_counts.get(prediction, 0) + 1

        if prev_r_peak is not None:
            rr_samples = r_peak_idx - prev_r_peak
            if rr_samples > 0:
                bpm_values.append(compute_bpm(rr_samples, fs))
                rr_ms_history.append(rr_to_ms(rr_samples, fs))
        prev_r_peak = r_peak_idx

        if prediction != NORMAL_LABEL:
            if len(anomalies) < max_anomalies:
                anomalies.append({
                    'beat_index': i,
                    'r_peak_sample': r_peak_idx,
                    'time_seconds': round(r_peak_idx / fs, 2),
                    'prediction': prediction,
                    'confidence': confidence,
                })

    total_beats = len(beats)
    total_anomaly_beats = total_beats - class_counts.get(NORMAL_LABEL, 0)

    class_percentages = {
        label: round(count / total_beats * 100, 2) if total_beats else 0.0
        for label, count in class_counts.items()
    }

    if bpm_values:
        bpm_stats = {
            'avg': round(float(np.mean(bpm_values)), 1),
            'min': round(float(np.min(bpm_values)), 1),
            'max': round(float(np.max(bpm_values)), 1),
        }
    else:
        bpm_stats = {'avg': 0.0, 'min': 0.0, 'max': 0.0}

    hrv_stats = {
        'sdnn_ms': round(compute_sdnn(rr_ms_history), 2),
        'rmssd_ms': round(compute_rmssd(rr_ms_history), 2),
    }

    if total_beats == 0:
        overall_assessment = (
            "Không phát hiện được nhịp tim nào trong tín hiệu tải lên. "
            "Vui lòng kiểm tra lại file hoặc tần số lấy mẫu (fs) đã khai báo."
        )
    elif total_anomaly_beats == 0:
        overall_assessment = f"Toàn bộ {total_beats} nhịp đều được phân loại BÌNH THƯỜNG."
    else:
        dominant_label, dominant_count = max(
            ((label, count) for label, count in class_counts.items() if label != NORMAL_LABEL),
            key=lambda kv: kv[1],
        )
        pct = round(total_anomaly_beats / total_beats * 100, 1)
        overall_assessment = (
            f"Phát hiện {total_anomaly_beats}/{total_beats} nhịp bất thường ({pct}%), "
            f"chủ yếu là '{dominant_label}' ({dominant_count} nhịp)."
        )

    return {
        'total_beats': total_beats,
        'duration_seconds': round(len(signal) / fs, 2),
        'class_counts': class_counts,
        'class_percentages': class_percentages,
        'bpm': bpm_stats,
        'hrv': hrv_stats,
        'anomalies': anomalies,
        'anomalies_total': total_anomaly_beats,
        'anomalies_truncated': total_anomaly_beats > max_anomalies,
        'overall_assessment': overall_assessment,
    }
