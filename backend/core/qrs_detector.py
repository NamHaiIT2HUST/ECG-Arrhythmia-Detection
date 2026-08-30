import numpy as np
from scipy.signal import find_peaks, resample

from backend.core.signal_processing import bandpass_filter

# Model duoc train tren bo du lieu Kaggle MIT-BIH heartbeat, da resample tin hieu ve 125Hz
# (khac voi 360Hz cua PhysioNet goc). Cat nhip o serving-time PHAI dua ve dung mien nay.
MODEL_FS = 125


def pan_tompkins_r_peaks(signal, fs=360):
    """Phat hien dinh R bang thuat toan Pan-Tompkins (rut gon).

    Cac buoc chuan: loc bandpass nhan pho QRS (5-15Hz) -> dao ham (nhan do doc)
    -> binh phuong (khuech dai + chi con gia tri duong) -> tich phan cua so
    truot ~150ms (gom nang luong QRS thanh 1 "buou") -> tim dinh voi nguong
    thich nghi + khoang cach toi thieu (refractory period ~200ms).

    Dinh tim duoc tren tin hieu da tich phan bi tre pha so voi dinh R that
    (do do tre cua bo loc + cua so tich phan), nen buoc cuoi se do lai dinh
    bien do lon nhat trong tin hieu GOC (`signal`) trong 1 khoang tim kiem
    nho quanh moi ung vien de bam sat dinh R thuc te.

    `signal` nen la tin hieu DA duoc loc nhieu duong nen/dien luoi truoc do
    (xem `signal_processing.bandpass_filter` / `notch_filter`) de tranh
    baseline wander lam sai lech nguong thich nghi.

    Tra ve: mang chi so cac dinh R (int, tang dan) trong `signal` goc.
    """
    signal = np.asarray(signal, dtype=np.float64)
    min_len = fs  # can toi thieu ~1s du lieu de nguong thich nghi co y nghia
    if len(signal) < min_len:
        return np.array([], dtype=int)

    # 1. Loc nhan pho QRS
    qrs_band = bandpass_filter(signal, lowcut=5.0, highcut=15.0, fs=fs, order=2)

    # 2. Dao ham (nhan manh do doc, dac trung cua phuc bo QRS)
    derivative = np.diff(qrs_band, prepend=qrs_band[0])

    # 3. Binh phuong
    squared = derivative ** 2

    # 4. Tich phan cua so truot ~150ms
    win_len = max(1, int(round(0.15 * fs)))
    kernel = np.ones(win_len) / win_len
    integrated = np.convolve(squared, kernel, mode='same')

    # 5. Nguong thich nghi (ty le theo bien do trung binh phan tin hieu > 0)
    #    + khoang cach toi thieu giua 2 dinh (~200ms, tuong ung nhip tim toi da 300 bpm)
    positive = integrated[integrated > 0]
    if positive.size == 0:
        return np.array([], dtype=int)
    threshold = 0.35 * np.mean(positive)
    min_distance = max(1, int(round(0.2 * fs)))

    candidate_peaks, _ = find_peaks(integrated, distance=min_distance, height=threshold)
    if candidate_peaks.size == 0:
        return np.array([], dtype=int)

    # 6. Hieu chinh lai vi tri dinh tren tin hieu GOC (bu tre pha cua buoc 1-4).
    # Ban dau dung +-40ms nhung do voi nhip That/Fusion (PVC) co QRS gian rong,
    # "buou" nang luong tren tin hieu tich phan lech xa dinh R that ~28-33 mau
    # (~78-92ms @360Hz) -> +-40ms khong voi toi. Da kiem chung thuc nghiem tren
    # 8 ban ghi MIT-BIH (so voi nhan bac si trong file .atr): +-120ms cho F1
    # trung binh ~97% (vd record 208 nhieu PVC: 72.96% -> 99.04%), trong khi
    # van an toan vi khoang cach toi thieu 2 dinh (`min_distance` ~200ms) lon
    # hon nhieu so voi vung chong lan co the xay ra giua 2 cua so tim kiem.
    search_radius = max(1, int(round(0.12 * fs)))  # +-120ms
    r_peaks = []
    for c in candidate_peaks:
        lo = max(0, c - search_radius)
        hi = min(len(signal), c + search_radius + 1)
        segment = signal[lo:hi]
        local_idx = lo + int(np.argmax(np.abs(segment - np.mean(segment))))
        r_peaks.append(local_idx)

    # Loai trung lap (2 ung vien co the hieu chinh ve cung 1 diem)
    return np.array(sorted(set(r_peaks)), dtype=int)


def resample_signal(signal, orig_fs, target_fs):
    """Resample TOAN BO 1 tin hieu lien tuc tu orig_fs sang target_fs (vd 360Hz -> 125Hz
    de khop tan so cua bo du lieu Kaggle MIT-BIH da dung luc train). Chi dung cho ca doan
    tin hieu dai lien tuc — KHONG dung ham nay cho tung nhip rieng le (xem canh bao trong
    `extract_beat_window`)."""
    signal = np.asarray(signal, dtype=np.float64)
    if orig_fs == target_fs:
        return signal
    num_samples = max(1, int(round(len(signal) * target_fs / orig_fs)))
    return resample(signal, num_samples)


def extract_beat_window(signal, r_peaks, index, window_size=187, fs=MODEL_FS, min_beat_ms=200):
    """Cat 1 nhip tim bat dau TAI dinh R, do dai dong toi da 1.2x khoang RR ke tiep,
    roi CAT BOT (neu dai hon window_size) hoac DEM SO 0 O CUOI - zero-pad (neu ngan hon)
    de duoc dung `window_size` diem.

    QUAN TRONG:ham nay KHONG resample/co dan tung nhip theo thoi gian — da thu resample
    tung nhip rieng le luc dau va kiem chung thuc te tren 8 ban ghi MIT-BIH cho ket qua
    RAT TE (Accuracy chi ~27%, F1-macro ~14%, so voi ~92% F1 luc benchmark offline), vi
    lam vay se boi/nen dang QRS that (khac han cach tao du lieu Kaggle: kiem tra truc tiep
    file `X_train_kaggle.npy` cho thay moi nhip co DUOI TOAN SO 0 — tuc la ho DEM (pad),
    khong co dan). Sau khi sua thanh pad/truncate: Accuracy tren du lieu that ~86%, F1-macro
    ~72% (xem `backend/scripts/validate_classification.py`).

    `signal` va `r_peaks` PHAI cung nam tren 1 truc thoi gian dung fs=`MODEL_FS` (125Hz) —
    dung `resample_signal()` de dua tin hieu goc (thuong 360Hz) ve dung mien nay truoc, va
    tu quy doi chi so dinh R tuong ung (xem `compute_all_beats`). Goi truc tiep ham nay voi
    tin hieu/dinh R con o 360Hz se cho ket qua sai.

    Tra ve mang float32 do dai `window_size`, hoac None neu khong du du lieu.
    """
    if index < 0 or index >= len(r_peaks):
        return None

    signal = np.asarray(signal, dtype=np.float64)
    r = int(r_peaks[index])
    min_len = max(1, int(round(min_beat_ms / 1000.0 * fs)))

    if index + 1 < len(r_peaks):
        rr_samples = int(r_peaks[index + 1]) - r
    elif index > 0:
        rr_samples = r - int(r_peaks[index - 1])
    else:
        rr_samples = int(round(0.8 * fs))  # khong co RR nao de tham chieu (~75 bpm)

    beat_len = max(int(round(rr_samples * 1.2)), min_len)
    end = min(r + beat_len, len(signal))
    beat = signal[r:end] if r < len(signal) else np.array([])

    if len(beat) == 0:
        return None

    if len(beat) >= window_size:
        beat = beat[:window_size]
    else:
        beat = np.pad(beat, (0, window_size - len(beat)))

    return beat.astype(np.float32)


def compute_all_beats(signal, fs=360, window_size=187, model_fs=MODEL_FS):
    """Tien ich: phat hien toan bo dinh R tren tin hieu GOC (fs, thuong 360Hz — noi thuat
    toan Pan-Tompkins da duoc kiem chung ~97% F1), roi resample TOAN BO tin hieu ve
    `model_fs` (125Hz, khop du lieu train) truoc khi cat tung nhip (khong resample rieng
    tung nhip — xem `extract_beat_window`). Dung cho benchmark/offline diagnosis (upload file)
    va co the tai su dung tung phan cho streaming.

    Tra ve list[(r_peak_idx_tren_tin_hieu_GOC, beat_window)] — chi so dinh R tra ve theo
    truc thoi gian GOC (fs) de con dung dong bo voi vi tri trong luong stream / tinh thoi
    gian thuc te, du ban than cua so `beat_window` da o mien 125Hz.
    """
    r_peaks_native = pan_tompkins_r_peaks(signal, fs=fs)
    if len(r_peaks_native) == 0:
        return []

    if fs != model_fs:
        model_signal = resample_signal(signal, fs, model_fs)
        scale = model_fs / fs
        r_peaks_model = np.clip(np.round(r_peaks_native * scale).astype(int), 0, len(model_signal) - 1)
    else:
        model_signal = np.asarray(signal, dtype=np.float64)
        r_peaks_model = r_peaks_native

    beats = []
    for i in range(len(r_peaks_model)):
        window = extract_beat_window(model_signal, r_peaks_model, i, window_size=window_size, fs=model_fs)
        if window is not None:
            beats.append((int(r_peaks_native[i]), window))
    return beats
