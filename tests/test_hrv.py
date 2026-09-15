from backend.core.hrv import HRVTracker, TACHYCARDIA_BPM_THRESHOLD, is_tachycardia

FS = 360


def _rr_samples_for_bpm(bpm, fs=FS):
    """Khoảng RR (số mẫu) tương ứng đúng 1 BPM cho trước."""
    return int(round((60.0 / bpm) * fs))


def test_is_tachycardia_false_when_not_enough_beats():
    rr_fast = [_rr_samples_for_bpm(150)] * 2  # chỉ 2 khoảng RR, chưa đủ TACHYCARDIA_MIN_BEATS
    assert is_tachycardia(rr_fast, fs=FS) is False


def test_is_tachycardia_true_for_sustained_fast_rate():
    rr_fast = [_rr_samples_for_bpm(150)] * 5
    assert is_tachycardia(rr_fast, fs=FS) is True


def test_is_tachycardia_false_for_normal_rate():
    rr_normal = [_rr_samples_for_bpm(75)] * 5
    assert is_tachycardia(rr_normal, fs=FS) is False


def test_is_tachycardia_ignores_single_beat_spike():
    """1 khoảng RR ngắn bất thường (VD ngoại tâm thu) không nên tự nó kích hoạt cảnh báo -
    trung bình cửa sổ trượt phải kéo xuống dưới ngưỡng."""
    rr_history = [_rr_samples_for_bpm(70)] * 4 + [_rr_samples_for_bpm(180)]
    assert is_tachycardia(rr_history, fs=FS) is False


def test_hrv_tracker_reports_tachycardia_suspected_field():
    tracker = HRVTracker(fs=FS)
    idx = 0
    result = {}
    for _ in range(6):
        idx += _rr_samples_for_bpm(150, fs=FS)
        result = tracker.update(idx)
    assert result["tachycardia_suspected"] is True
    assert result["bpm"] >= TACHYCARDIA_BPM_THRESHOLD
