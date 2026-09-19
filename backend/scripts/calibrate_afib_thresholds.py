#!/usr/bin/env python3
"""Hiệu chỉnh ngưỡng AFib trên dữ liệu AFDB đã tải về — dùng nhãn nhịp điệu THẬT.

BẢN SỬA (nói thật lý do sửa): bản trước giả định *toàn bộ* bản ghi AFDB tải về đều
là rung nhĩ (không đọc annotation), khiến "specificity" luôn tính ra bằng 0 và
ngưỡng "tối ưu" tìm được không có ý nghĩa thống kê thật — chỉ là demo cơ chế đo.
Bản này sửa đúng gốc rễ:
  1. Đọc nhãn nhịp điệu THẬT từ file `.atr` (annotation rhythm, vd `(AFIB`, `(N`,
     `(AFL`, `(J`) thay vì giả định tất cả là AFib.
  2. Dùng lại đúng bộ dò đỉnh R đã kiểm chứng 97.14% F1 (`pan_tompkins_r_peaks`,
     xem `backend/scripts/validate_qrs.py`) thay vì bộ dò thô sơ tự chế trước đây
     (đỉnh cực đại mỗi cửa sổ 0.6s cố định) — RR-interval sai lệch sẽ kéo sai mọi
     chỉ số AFib phái sinh từ nó.
  3. Chạy ĐÚNG class `AfibScreener` sản phẩm (không tự chế lại công thức riêng
     trong script), để ngưỡng tìm được phản ánh đúng hành vi hệ thống thật đang
     dùng trong `backend/api/ws_routes.py`.

Kết quả in ra là Sensitivity/Specificity thật theo từng ngưỡng (đường ROC thô) và
ngưỡng đề xuất theo Youden's J (sens + spec - 1 lớn nhất) — có thể dùng để cập nhật
`AfibScreener.threshold`.

Ví dụ:
    python -m backend.scripts.calibrate_afib_thresholds --afdb-dir data/raw/afdb
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import wfdb

from backend.core.afib_screener import AfibScreener
from backend.core.qrs_detector import pan_tompkins_r_peaks
from backend.core.signal_processing import bandpass_filter, notch_filter

# AFDB dùng nhãn rung nhĩ đúng nghĩa là "(AFIB" — "(AFL" (cuồng nhĩ) và "(J" (nhịp bộ
# nối) là 2 rối loạn nhịp KHÁC, cố tình không tính là dương tính để không thổi phồng
# sensitivity một cách giả tạo (AfibScreener chỉ được thiết kế để sàng lọc AFib).
POSITIVE_RHYTHM_PREFIXES = ("AFIB",)


def _load_rhythm_segments(record_path: Path) -> list[tuple[int, str]]:
    """Đọc các điểm đổi nhịp điệu từ annotation `.atr` (symbol '+', aux_note dạng
    "(AFIB\\x00", "(N\\x00"...). Trả về list (sample_bắt_đầu, tên_nhịp) đã sort."""
    ann = wfdb.rdann(str(record_path.with_suffix("")), "atr")
    segments: list[tuple[int, str]] = []
    for sample, aux in zip(ann.sample, ann.aux_note):
        note = (aux or "").strip("\x00").strip()
        if note.startswith("("):
            segments.append((int(sample), note[1:]))
    segments.sort(key=lambda x: x[0])
    return segments


def _rhythm_label_at(segments: list[tuple[int, str]], sample: int) -> str:
    """Nhịp điệu có hiệu lực tại 1 sample cụ thể — segments đã sort nên chỉ cần lấy
    đoạn cuối cùng có sample_bắt_đầu <= sample."""
    label = "N"
    for seg_sample, seg_label in segments:
        if seg_sample <= sample:
            label = seg_label
        else:
            break
    return label


def _evaluate_record(record_path: Path) -> tuple[list[float], list[int]]:
    """Chạy pipeline THẬT (lọc -> Pan-Tompkins -> AfibScreener, đúng như
    `data_streamer.py` làm real-time) trên 1 record AFDB, trả về song song
    (afib_score, nhãn_thật) tại từng đỉnh R phát hiện được."""
    signal, fields = wfdb.rdsamp(str(record_path.with_suffix("")), channels=[0])
    signal = np.asarray(signal, dtype=np.float64).reshape(-1)
    fs = float(fields.get("fs", 250))

    segments = _load_rhythm_segments(record_path)
    if not segments:
        print(f"  [SKIP] {record_path.name}: không có annotation nhịp điệu.")
        return [], []

    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    r_peaks = pan_tompkins_r_peaks(clean, fs=fs)

    screener = AfibScreener(fs=fs)
    scores: list[float] = []
    labels: list[int] = []
    for r_peak in r_peaks:
        result = screener.update(int(r_peak))
        rhythm = _rhythm_label_at(segments, int(r_peak))
        is_afib = 1 if rhythm.upper().startswith(POSITIVE_RHYTHM_PREFIXES) else 0
        scores.append(float(result["afib_score"]))
        labels.append(is_afib)
    return scores, labels


def _evaluate_thresholds(afdb_dir: Path) -> None:
    if not afdb_dir.exists():
        print(f"[WARN] Không tìm thấy {afdb_dir}. Hãy chạy: python -m backend.scripts.download_afdb_sample")
        return

    dat_files = sorted(afdb_dir.glob("*.dat"))
    if not dat_files:
        print(f"[WARN] Không có file .dat trong {afdb_dir}. Hãy chạy: python -m backend.scripts.download_afdb_sample")
        return

    all_scores: list[float] = []
    all_labels: list[int] = []
    rhythms_seen: dict[str, int] = {}

    for dat_file in dat_files:
        try:
            scores, labels = _evaluate_record(dat_file)
        except Exception as exc:
            print(f"  [LỖI] {dat_file.name}: {exc}")
            continue
        n_pos = sum(labels)
        print(f"  {dat_file.stem}: {len(scores)} đỉnh R, {n_pos} nhãn AFIB thật ({n_pos / len(labels) * 100:.1f}%)" if labels else f"  {dat_file.stem}: rỗng")
        all_scores.extend(scores)
        all_labels.extend(labels)

    if not all_scores:
        print("[WARN] Không có dữ liệu hợp lệ để calibrate.")
        return

    n_pos_total = sum(all_labels)
    n_neg_total = len(all_labels) - n_pos_total
    print(f"\n[TỔNG] {len(all_labels)} đỉnh R — {n_pos_total} AFIB thật ({n_pos_total / len(all_labels) * 100:.1f}%), {n_neg_total} không phải AFIB.")
    if n_pos_total == 0 or n_neg_total == 0:
        print("[WARN] Dữ liệu chỉ có 1 lớp (toàn AFIB hoặc toàn không-AFIB) — không tính được ROC có ý nghĩa."
              " Cần tải thêm record AFDB có cả 2 loại nhịp (vd 04015, 04043 đều có đoạn N xen kẽ AFIB).")
        return

    scores_arr = np.asarray(all_scores)
    labels_arr = np.asarray(all_labels)

    thresholds = np.linspace(0.0, 1.0, 101)
    rows = []
    best = None
    for th in thresholds:
        pred = scores_arr >= th
        tp = int(np.sum(pred & (labels_arr == 1)))
        tn = int(np.sum((~pred) & (labels_arr == 0)))
        fp = int(np.sum(pred & (labels_arr == 0)))
        fn = int(np.sum((~pred) & (labels_arr == 1)))
        sens = tp / (tp + fn) if (tp + fn) else 0.0
        spec = tn / (tn + fp) if (tn + fp) else 0.0
        youden_j = sens + spec - 1.0
        rows.append((th, sens, spec, youden_j, tp, tn, fp, fn))
        if best is None or youden_j > best[3]:
            best = (th, sens, spec, youden_j, tp, tn, fp, fn)

    print("\n[ROC — vài điểm mốc]")
    print(f"{'ngưỡng':>8} {'sens':>8} {'spec':>8} {'Youden J':>10}")
    for th, sens, spec, yj, *_ in rows[::10]:
        print(f"{th:8.2f} {sens:8.3f} {spec:8.3f} {yj:10.3f}")

    th, sens, spec, yj, tp, tn, fp, fn = best
    print("\n[NGƯỠNG ĐỀ XUẤT — theo Youden's J lớn nhất]")
    print(f"  threshold: {th:.3f}")
    print(f"  sensitivity: {sens:.3f}  (bắt đúng {tp}/{tp + fn} nhịp AFIB thật)")
    print(f"  specificity: {spec:.3f}  (bắt đúng {tn}/{tn + fp} nhịp không-AFIB)")
    print(f"  Youden's J: {yj:.3f}")
    print(f"  tp/tn/fp/fn: {tp}/{tn}/{fp}/{fn}")
    print("\n[OK] Đây là số liệu thật, có thể dùng để cập nhật AfibScreener.threshold"
          " (backend/core/afib_screener.py) một cách có căn cứ thống kê.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hiệu chỉnh ngưỡng cho module AFib screening bằng nhãn nhịp điệu thật.")
    parser.add_argument("--afdb-dir", type=str, default="data/raw/afdb", help="Thư mục chứa AFDB đã tải xuống.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _evaluate_thresholds(Path(args.afdb_dir))


if __name__ == "__main__":
    main()
