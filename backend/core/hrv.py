import numpy as np

# Nguong nhip nhanh bat thuong (tachycardia) o nguoi lon khi nghi - chuan lam sang pho bien:
# nhip tim > 100 bpm. Dung trung binh vai nhip gan nhat (khong phai tuc thoi 1 nhip) de tranh
# bao dong gia tu 1 nhip le/nhieu don le (VD 1 ngoai tam thu lam RR ngan bat thuong).
TACHYCARDIA_BPM_THRESHOLD = 100.0
TACHYCARDIA_MIN_BEATS = 3  # can it nhat 3 khoang RR gan nhat de tinh trung binh co y nghia

# So khoang RR gan nhat dung de tinh BPM HIEN THI (trung binh, khong phai tuc thoi) - BPM tuc
# thoi tu dung 1 khoang RR dao dong binh thuong theo sinh ly (ho hap, 1 ngoai tam thu don le...)
# khien so hien tren man hinh "nhay loan" (vd 76 -> 100 -> 120) du nguoi benh khong thay doi
# nhip that. Trung binh vai nhip gan nhat cho so on dinh, de doc hon, giong cach may monitor
# that hien thi HR (khong anh huong is_tachycardia() - ham do da tu tinh trung binh rieng).
BPM_DISPLAY_WINDOW = 6


def rr_to_ms(rr_samples, fs=360):
    """Doi 1 khoang RR (so mau) sang mili-giay."""
    return (rr_samples / fs) * 1000.0


def compute_bpm(rr_samples, fs=360):
    """Nhip tim tuc thoi (BPM) tu 1 khoang RR (so mau).
    BPM = 60 / RR(giay). Tra ve 0.0 neu RR khong hop le (<=0)."""
    if rr_samples is None or rr_samples <= 0:
        return 0.0
    rr_seconds = rr_samples / fs
    return 60.0 / rr_seconds


def compute_sdnn(rr_intervals_ms):
    """SDNN: do lech chuan cua cac khoang RR (ms) — chi so HRV co ban, phan anh
    bien thien nhip tim tong the. Can it nhat 2 khoang RR de tinh duoc."""
    if len(rr_intervals_ms) < 2:
        return 0.0
    return float(np.std(np.asarray(rr_intervals_ms, dtype=np.float64), ddof=1))


def compute_rmssd(rr_intervals_ms):
    """RMSSD: can bac 2 trung binh binh phuong hieu 2 khoang RR lien tiep (ms) —
    nhay voi bien thien nhip tim ngan han (dieu hoa boi than kinh phe vi).
    Can it nhat 3 khoang RR (2 hieu so) de tinh duoc."""
    rr = np.asarray(rr_intervals_ms, dtype=np.float64)
    if len(rr) < 3:
        return 0.0
    diffs = np.diff(rr)
    return float(np.sqrt(np.mean(diffs ** 2)))


def is_tachycardia(rr_samples_history, fs=360, window=5,
                    threshold_bpm=TACHYCARDIA_BPM_THRESHOLD, min_beats=TACHYCARDIA_MIN_BEATS):
    """Nghi ngo nhip nhanh bat thuong: BPM trung binh cua `window` khoang RR gan nhat vuot
    nguong. Dung trung binh (khong phai BPM tuc thoi 1 nhip) de on dinh hon truoc nhieu/
    ngoai tam thu don le. Can it nhat `min_beats` khoang RR moi bat dau danh gia."""
    recent = rr_samples_history[-window:]
    if len(recent) < min_beats:
        return False
    avg_bpm = float(np.mean([compute_bpm(rr, fs) for rr in recent]))
    return avg_bpm >= threshold_bpm


class HRVTracker:
    """Theo doi lich su khoang RR gan nhat de tinh BPM tuc thoi + HRV theo cua so truot.
    Moi ket noi WebSocket/stream nen co 1 instance rieng (khong dung chung global state)."""

    def __init__(self, fs=360, max_history=50):
        self.fs = fs
        self.max_history = max_history
        self._rr_samples_history = []
        self._last_r_peak = None

    def update(self, r_peak_idx):
        """Goi moi khi phat hien 1 dinh R moi (chi so mau, tinh lien tuc trong toan ban ghi).
        Tra ve dict {bpm, sdnn, rmssd} tinh tai thoi diem nay (0.0 neu chua du du lieu)."""
        if self._last_r_peak is not None:
            rr = r_peak_idx - self._last_r_peak
            if rr > 0:
                self._rr_samples_history.append(rr)
                if len(self._rr_samples_history) > self.max_history:
                    self._rr_samples_history.pop(0)
        self._last_r_peak = r_peak_idx

        if not self._rr_samples_history:
            return {'bpm': 0.0, 'hrv_sdnn': 0.0, 'hrv_rmssd': 0.0, 'tachycardia_suspected': False}

        rr_ms_history = [rr_to_ms(rr, self.fs) for rr in self._rr_samples_history]
        recent_rr = self._rr_samples_history[-BPM_DISPLAY_WINDOW:]
        bpm = float(np.mean([compute_bpm(rr, self.fs) for rr in recent_rr]))
        return {
            'bpm': round(bpm, 1),
            'hrv_sdnn': round(compute_sdnn(rr_ms_history), 2),
            'hrv_rmssd': round(compute_rmssd(rr_ms_history), 2),
            'tachycardia_suspected': is_tachycardia(self._rr_samples_history, self.fs),
        }
