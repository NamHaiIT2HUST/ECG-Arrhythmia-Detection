import os
import time
import asyncio
import wfdb

import numpy as np

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import pan_tompkins_r_peaks, extract_beat_window, resample_signal, MODEL_FS
from backend.core.hrv import HRVTracker
from backend.core.afib_screener import AfibScreener

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

    Mỗi lần lặp trả về (chunk, chunk2, beat_info, lead1_name, lead2_name):
    - chunk: list `chunk_size` giá trị (đã lọc nhiễu) của kênh 0 - kênh DUY NHẤT dùng để phát
      hiện đỉnh R và chạy AI (không đổi hành vi chẩn đoán so với trước).
    - chunk2: list `chunk_size` giá trị của kênh 1 nếu bản ghi có ≥2 kênh (đa số MIT-BIH), chỉ
      dùng để hiển thị thêm dải sóng tham chiếu trên Dashboard; None nếu bản ghi chỉ có 1 kênh.
    - beat_info: None nếu gói tin này không chứa đỉnh R nào; ngược lại là dict
      {'window': ndarray(window_size,), 'bpm': float, 'hrv_sdnn': float, 'hrv_rmssd': float}
      — chỉ được tạo đúng 1 lần mỗi nhịp tim thật (không chạy AI liên tục trên mọi gói tin).
    - lead1_name/lead2_name: tên kênh theo header PhysioNet (vd 'MLII', 'V1'), lead2_name=None
      nếu bản ghi chỉ có 1 kênh.
    """
    delay_s = 1.0 / fps

    abs_filepath = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath

    if not os.path.exists(abs_filepath + ".dat"):
        print(f"[!] Không tìm thấy file gốc {abs_filepath}.dat. Vui lòng tải data MIT-BIH trước.")
        while True:
            yield [0.0] * chunk_size, None, None, 'Lead 1', None
            await asyncio.sleep(delay_s)
        return

    try:
        # Đọc TẤT CẢ kênh có sẵn (đa số bản ghi MIT-BIH có 2 kênh, vd MLII + V1/V5) thay vì chỉ
        # channels=[0] như trước - kênh 0 vẫn là kênh DUY NHẤT dùng để phát hiện đỉnh R/chạy AI
        # (không đổi hành vi chẩn đoán), kênh 1 (nếu có) chỉ dùng để hiển thị thêm 1 dải sóng
        # tham chiếu trên Dashboard, giống quy ước máy Holter 2 kênh thật - xem ECGChart.jsx.
        signals_all, fields = wfdb.rdsamp(abs_filepath)
        sig_names = fields.get('sig_name') or []
        signals = signals_all[:, 0]
        has_lead2 = signals_all.shape[1] > 1
        signals2 = signals_all[:, 1] if has_lead2 else None
        lead1_name = sig_names[0] if len(sig_names) > 0 else 'Lead 1'
        lead2_name = sig_names[1] if has_lead2 and len(sig_names) > 1 else None
        fs = fields.get('fs', 360)
    except Exception as e:
        print(f"[!] Lỗi đọc wfdb: {e}")
        return

    # Lọc nhiễu (bandpass 0.5-45Hz + notch 50Hz) 1 lần cho toàn bộ tín hiệu
    clean_signal = notch_filter(bandpass_filter(signals, fs=fs), fs=fs)
    clean_signal2 = notch_filter(bandpass_filter(signals2, fs=fs), fs=fs) if has_lead2 else None

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
    # AfibScreener song song HRVTracker, cung reset khi loop lai tu dau (xem nhanh idx>=len
    # ben duoi) - truoc day AfibScreener duoc tao rieng o ws_routes.py va KHONG bao gio duoc
    # reset khi stream lap lai, khien lich su RR cua no bi "bac cau" giua cuoi va dau ban ghi,
    # lam afib_score sai lech trong vai chuc nhip dau moi vong lap tren ket noi chay lau.
    afib_screener = AfibScreener(fs=fs)

    while True:
        chunk = []
        chunk2 = [] if has_lead2 else None
        beat_info = None

        for _ in range(chunk_size):
            if idx >= len(signals):
                idx = 0
                beat_cursor = 0
                tracker = HRVTracker(fs=fs)  # Loop lại từ đầu để demo chạy mãi mãi
                afib_screener = AfibScreener(fs=fs)

            val = float(clean_signal[idx])
            chunk.append(val)
            if has_lead2:
                chunk2.append(float(clean_signal2[idx]))

            if beat_cursor < len(r_peaks) and idx == r_peaks[beat_cursor]:
                window = extract_beat_window(model_signal, r_peaks_model, beat_cursor, window_size=window_size, fs=MODEL_FS)
                if window is not None:
                    hrv = tracker.update(int(r_peaks[beat_cursor]))
                    afib = afib_screener.update(int(r_peaks[beat_cursor]))
                    # 'detected_at': moc thoi gian ngay luc phat hien nhip nay - dung de do
                    # End-to-End Latency (xem ws_routes.py va benchmark_e2e_latency.py).
                    beat_info = {'window': window, 'r_peak_sample': int(r_peaks[beat_cursor]),
                                 'detected_at': time.time(), **hrv,
                                 'afib_suspected': afib['afib_suspected'], 'afib_score': afib['afib_score']}
                beat_cursor += 1

            idx += 1

        yield chunk, chunk2, beat_info, lead1_name, lead2_name

        await asyncio.sleep(delay_s)
