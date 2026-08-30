import os
import asyncio
import wfdb

import numpy as np

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import pan_tompkins_r_peaks, extract_beat_window, resample_signal, MODEL_FS
from backend.core.hrv import HRVTracker

# Resolve đường dẫn tuyệt đối từ vị trí file này
# Tránh bị lỗi khi chạy uvicorn từ thư mục khác
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def ecg_file_reader(filepath="data/raw/physionet_mitdb/208", chunk_size=10, fps=36, window_size=187):
    """
    Giả lập máy điện tim đọc liên tục từ file tín hiệu PhysioNet.
    - chunk_size: Gửi bao nhiêu điểm trong 1 gói tin (mặc định 10 điểm).
    - fps: Tốc độ gửi gói tin (36 lần/giây x 10 điểm = 360 điểm/giây, bằng đúng tần số chuẩn của MIT-BIH).

    CP3: Thay vì dùng bộ đệm trượt 187 điểm thô (dễ cắt lệch đỉnh QRS khi nhịp tim
    thay đổi), giờ lọc nhiễu (bandpass + notch) 1 lần cho toàn bộ bản ghi, phát hiện
    TOÀN BỘ đỉnh R bằng Pan-Tompkins (backend/core/qrs_detector.py), rồi mỗi khi luồng
    "đi qua" 1 đỉnh R mới sẽ cắt đúng 1 nhịp bắt đầu từ đỉnh đó (độ dài động theo
    khoảng RR thực tế) và resample về đúng `window_size` điểm để khớp miền dữ liệu
    đã dùng lúc train (xem plan.md mục 3.0).

    Mỗi lần lặp trả về (chunk, beat_info):
    - chunk: list `chunk_size` giá trị (đã lọc nhiễu) để vẽ biểu đồ liên tục.
    - beat_info: None nếu gói tin này không chứa đỉnh R nào; ngược lại là dict
      {'window': ndarray(window_size,), 'bpm': float, 'hrv_sdnn': float, 'hrv_rmssd': float}
      — chỉ được tạo đúng 1 lần mỗi nhịp tim thật (không chạy AI liên tục trên mọi gói tin).
    """
    delay_s = 1.0 / fps

    abs_filepath = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath

    if not os.path.exists(abs_filepath + ".dat"):
        print(f"[!] Không tìm thấy file gốc {abs_filepath}.dat. Vui lòng tải data MIT-BIH trước.")
        while True:
            yield [0.0] * chunk_size, None
            await asyncio.sleep(delay_s)
        return

    try:
        signals, fields = wfdb.rdsamp(abs_filepath, channels=[0])
        signals = signals.flatten()
        fs = fields.get('fs', 360)
    except Exception as e:
        print(f"[!] Lỗi đọc wfdb: {e}")
        return

    # Lọc nhiễu (bandpass 0.5-45Hz + notch 50Hz) 1 lần cho toàn bộ tín hiệu
    clean_signal = notch_filter(bandpass_filter(signals, fs=fs), fs=fs)

    # Phát hiện toàn bộ đỉnh R 1 lần cho cả bản ghi, trên tín hiệu GỐC (fs, thường 360Hz —
    # nơi thuật toán Pan-Tompkins đã được kiểm chứng ~97% F1 so với nhãn bác sĩ)
    r_peaks = pan_tompkins_r_peaks(clean_signal, fs=fs)
    print(f"[+] Đã phát hiện {len(r_peaks)} đỉnh R trong bản ghi ({len(signals)} điểm, {fs}Hz).")

    # Resample TOÀN BỘ tín hiệu về đúng miền dữ liệu train (MODEL_FS=125Hz, xem
    # qrs_detector.py) 1 lần duy nhất, và quy đổi chỉ số đỉnh R sang miền này.
    # extract_beat_window() cắt nhịp trên miền 125Hz này (đệm số 0/cắt bớt, KHÔNG resample
    # riêng từng nhịp — xem docstring extract_beat_window để biết lý do).
    model_signal = resample_signal(clean_signal, fs, MODEL_FS)
    r_peaks_model = np.clip(np.round(r_peaks * (MODEL_FS / fs)).astype(int), 0, len(model_signal) - 1)

    print(f"[+] Bắt đầu phát sóng stream ({fps} FPS), tổng {len(signals)} điểm...")

    idx = 0
    beat_cursor = 0
    tracker = HRVTracker(fs=fs)

    while True:
        chunk = []
        beat_info = None

        for _ in range(chunk_size):
            if idx >= len(signals):
                idx = 0
                beat_cursor = 0
                tracker = HRVTracker(fs=fs)  # Loop lại từ đầu để demo chạy mãi mãi

            val = float(clean_signal[idx])
            chunk.append(val)

            if beat_cursor < len(r_peaks) and idx == r_peaks[beat_cursor]:
                window = extract_beat_window(model_signal, r_peaks_model, beat_cursor, window_size=window_size, fs=MODEL_FS)
                if window is not None:
                    hrv = tracker.update(int(r_peaks[beat_cursor]))
                    beat_info = {'window': window, **hrv}
                beat_cursor += 1

            idx += 1

        yield chunk, beat_info

        await asyncio.sleep(delay_s)
