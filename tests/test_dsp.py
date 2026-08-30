import numpy as np

from backend.core.signal_processing import bandpass_filter, normalize_window, notch_filter

FS = 360
DURATION_S = 10.0  # đủ dài để FFT có độ phân giải tần số mịn (0.1Hz) cho các test tần số thấp


def _tone(freq_hz, fs=FS, duration_s=DURATION_S, amplitude=1.0):
    t = np.arange(0, duration_s, 1 / fs)
    return amplitude * np.sin(2 * np.pi * freq_hz * t)


def _band_energy(signal, lo_hz, hi_hz, fs=FS):
    """Tổng biên độ phổ FFT trong 1 dải tần [lo_hz, hi_hz] — dùng dải thay vì 1 bin đơn lẻ
    để không phụ thuộc việc tần số cần đo có trùng khớp chính xác 1 bin FFT hay không."""
    freqs = np.fft.rfftfreq(len(signal), d=1 / fs)
    spectrum = np.abs(np.fft.rfft(signal))
    return spectrum[(freqs >= lo_hz) & (freqs <= hi_hz)].sum()


def test_bandpass_filter_removes_high_frequency_noise():
    # 10Hz (trong dải thông 0.5-45Hz) + 100Hz (ngoài dải, giả lập nhiễu cơ EMG tần số cao)
    signal = _tone(10) + _tone(100, amplitude=0.5)
    filtered = bandpass_filter(signal, lowcut=0.5, highcut=45.0, fs=FS)

    assert _band_energy(filtered, 95, 105) < _band_energy(signal, 95, 105) * 0.25
    assert _band_energy(filtered, 8, 12) > _band_energy(signal, 8, 12) * 0.5


def test_bandpass_filter_removes_baseline_wander():
    # 10Hz tín hiệu thật + 0.1Hz giả lập trôi đường nền (baseline wander, ngoài dải dưới 0.5Hz)
    signal = _tone(10) + _tone(0.1, amplitude=2.0)
    filtered = bandpass_filter(signal, lowcut=0.5, highcut=45.0, fs=FS)

    assert _band_energy(filtered, 0, 0.4) < _band_energy(signal, 0, 0.4) * 0.25
    assert _band_energy(filtered, 8, 12) > _band_energy(signal, 8, 12) * 0.5


def test_notch_filter_removes_mains_hum():
    signal = _tone(10) + _tone(50, amplitude=1.0)  # nhiễu điện lưới 50Hz
    filtered = notch_filter(signal, cutoff=50.0, q=30.0, fs=FS)

    assert _band_energy(filtered, 49, 51) < _band_energy(signal, 49, 51) * 0.25
    assert _band_energy(filtered, 8, 12) > _band_energy(signal, 8, 12) * 0.5


def test_normalize_window_range():
    window = np.array([-5.0, 0.0, 3.0, 10.0, -2.0])
    normalized = normalize_window(window)
    assert normalized.min() == 0.0
    assert normalized.max() == 1.0
    assert normalized.dtype == np.float32


def test_normalize_window_flat_signal_returns_zeros():
    """Tránh chia cho 0 khi tín hiệu hoàn toàn phẳng (span = 0)."""
    flat = np.full(50, 3.0)
    normalized = normalize_window(flat)
    assert np.all(normalized == 0.0)
