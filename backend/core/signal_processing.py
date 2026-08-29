import numpy as np
from scipy.signal import butter, filtfilt, iirnotch


def bandpass_filter(signal, lowcut=0.5, highcut=45.0, fs=360, order=4):
    """Loc bang thong Butterworth, loai bo troi duong nen (baseline wander) va nhieu tan so cao."""
    signal = np.asarray(signal, dtype=np.float64)
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)


def notch_filter(signal, cutoff=50.0, q=30.0, fs=360):
    """Loc khu nhieu dien luoi (mains hum) tai tan so cutoff (50Hz/60Hz)."""
    signal = np.asarray(signal, dtype=np.float64)
    nyq = 0.5 * fs
    w0 = cutoff / nyq
    b, a = iirnotch(w0, q)
    return filtfilt(b, a, signal)


def normalize_window(window):
    """Chuan hoa min-max mot cua so tin hieu ve dai [0, 1], khop voi mien du lieu da dung de train model
    (Kaggle MIT-BIH heartbeat dataset duoc chuan hoa bien do ve [0, 1])."""
    window = np.asarray(window, dtype=np.float64)
    w_min, w_max = window.min(), window.max()
    span = w_max - w_min
    if span < 1e-8:
        return np.zeros_like(window, dtype=np.float32)
    return ((window - w_min) / span).astype(np.float32)


def preprocess_window(window, fs=360):
    """Pipeline day du: loc bandpass + notch + chuan hoa bien do, dung truoc khi dua vao model.
    Ap dung tren tung cua so 187 diem de dam bao nhat quan giua moi nguon du lieu goi vao (stream, batch, test)."""
    filtered = bandpass_filter(window, fs=fs)
    filtered = notch_filter(filtered, fs=fs)
    return normalize_window(filtered)
