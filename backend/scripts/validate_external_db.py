"""
Ban tong quat hoa cua validate_external_incart.py - kiem chung model production (dang trien
khai tren dashboard real-time) tren BAT KY database PhysioNet nao khac MIT-BIH, khong can
sua code, chi truyen ten thu muc + kenh dao trinh + danh sach ban ghi.

Dung lai dung pipeline that (loc nhieu -> Pan-Tompkins -> resample 125Hz -> ResNet1D) qua
backend.core.qrs_detector.compute_all_beats + backend.service.inference_service.ai_service.

Chay:
    python -m backend.scripts.validate_external_db --data-dir data/raw/svdb --channel 0 \
        --records 822 892 854 870 863 823 --name SVDB
"""
import argparse

import numpy as np
import wfdb
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from backend.core.qrs_detector import compute_all_beats
from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.service.inference_service import ai_service

AAMI_CLASSES = {
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,
    "A": 1, "a": 1, "J": 1, "S": 1,
    "V": 2, "E": 2,
    "F": 3,
    "/": 4, "f": 4, "Q": 4,
}
IDX2LABEL = {
    0: "BÌNH THƯỜNG",
    1: "CẢNH BÁO: TRÊN THẤT (S)",
    2: "CẢNH BÁO: NHỊP THẤT (V)",
    3: "CẢNH BÁO: HỢP NHẤT (F)",
    4: "CẢNH BÁO: CHƯA RÕ (Q)",
}
LABEL2IDX = {v: k for k, v in IDX2LABEL.items()}
LABEL_NAMES = ["N", "S", "V", "F", "Q"]


def evaluate_record(record_id, data_dir, channel, tol_ms=75):
    path = f"{data_dir}/{record_id}"
    signals, fields = wfdb.rdsamp(path, channels=[channel])
    fs = fields["fs"]
    signal = signals.flatten()

    ann = wfdb.rdann(path, "atr")
    gt_samples = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in AAMI_CLASSES])
    gt_labels = np.array([AAMI_CLASSES[sym] for sym in ann.symbol if sym in AAMI_CLASSES])
    if gt_samples.size == 0:
        return np.array([]), np.array([])

    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    beats = compute_all_beats(clean, fs=fs)

    tol = int(tol_ms / 1000 * fs)
    y_true, y_pred = [], []
    for r_idx, window in beats:
        diffs = np.abs(gt_samples - r_idx)
        j = int(np.argmin(diffs)) if len(diffs) else None
        if j is None or diffs[j] > tol:
            continue
        pred_text, _heatmap, _latency, _confidence = ai_service.predict(window)
        y_true.append(gt_labels[j])
        y_pred.append(LABEL2IDX.get(pred_text, -1))

    return np.array(y_true), np.array(y_pred)


def parse_args():
    parser = argparse.ArgumentParser(description="Kiểm chứng generalization trên 1 database PhysioNet bất kỳ.")
    parser.add_argument("--data-dir", required=True, help="VD: data/raw/svdb")
    parser.add_argument("--channel", type=int, default=0, help="Chỉ số kênh đạo trình (0-based)")
    parser.add_argument("--records", nargs="+", required=True, help="Danh sách record ID")
    parser.add_argument("--name", default="DB", help="Tên hiển thị cho database")
    parser.add_argument("--model", default="saved_models/resnet1d.pth")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ai_service.load_model(args.model)

    print("=" * 70)
    print(f"KIỂM CHỨNG GENERALIZATION — {args.name} (channel={args.channel})")
    print("=" * 70)

    all_true, all_pred = [], []
    print(f"{'Record':<10}{'N':>7}{'Accuracy':>12}{'F1(macro)':>12}")
    for rec in args.records:
        try:
            y_true, y_pred = evaluate_record(rec, args.data_dir, args.channel)
        except FileNotFoundError:
            print(f"[!] Bỏ qua {rec}: chưa tải dữ liệu.")
            continue
        if len(y_true) == 0:
            print(f"[!] Bỏ qua {rec}: không khớp được nhịp GT nào.")
            continue
        acc = accuracy_score(y_true, y_pred)
        _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        print(f"{rec:<10}{len(y_true):>7}{acc*100:>11.2f}%{f1*100:>11.2f}%")
        all_true.extend(y_true.tolist())
        all_pred.extend(y_pred.tolist())

    if all_true:
        all_true = np.array(all_true)
        all_pred = np.array(all_pred)
        acc = accuracy_score(all_true, all_pred)
        cm = confusion_matrix(all_true, all_pred, labels=[0, 1, 2, 3, 4])
        print(f"\nTỔNG HỢP {args.name}: n={len(all_true)}  Accuracy={acc*100:.2f}%")
        print("Recall theo lớp (chỉ lớp có mặt trong GT):")
        for i, name in enumerate(LABEL_NAMES):
            support = int((all_true == i).sum())
            if support == 0:
                continue
            recall_i = float((all_pred[all_true == i] == i).mean())
            print(f"  {name}: Recall={recall_i*100:.1f}%  (n={support})")
        print("\nConfusion matrix (hàng=thật, cột=dự đoán) [N,S,V,F,Q]:")
        print(cm)
    else:
        print("\n[!] Không có dữ liệu hợp lệ nào để đánh giá.")
