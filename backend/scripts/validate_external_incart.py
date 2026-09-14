"""
Kiem chung tong quat hoa (generalization) tren du lieu HOAN TOAN chua tung thay: St
Petersburg INCART 12-lead Arrhythmia Database (PhysioNet) - khac benh vien, khac may do,
khac fs (257Hz thay vi 360Hz), khac dao (12 dao thay vi 2 dao Holter) so voi MIT-BIH dung
de train/test/validate xuyen suot du an. Muc dich: neu accuracy tren INCART van cao gan
bang MIT-BIH thi la bang chung manh cho generalization that (khong phai hoc thuoc dac diem
rieng cua thiet bi/benh vien MIT-BIH); neu tut manh thi can bao cao trung thuc, khong tô hồng.

Dung lai dung pipeline that (loc nhieu -> Pan-Tompkins -> resample 125Hz -> ResNet1D) qua
backend.core.qrs_detector.compute_all_beats + backend.service.inference_service.ai_service
- giong het validate_classification.py, chi khac data_dir va channel dao (dung Lead II,
idx=1, gan tuong duong ve mat giai phau voi MLII cua MIT-BIH, thay vi Lead I mac dinh idx=0).

Chay:
    python backend/scripts/download_external_incart.py   # tai du lieu truoc
    python -m backend.scripts.validate_external_incart
"""
import sys

import numpy as np
import wfdb
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from backend.core.qrs_detector import compute_all_beats
from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.service.inference_service import ai_service

DEFAULT_RECORDS = ["I01", "I15", "I30", "I45", "I60"]
DATA_DIR = "data/raw/incartdb"
LEAD_II_CHANNEL = 1  # xem header .hea: kenh 0=I, 1=II, 2=III, ... — dung Lead II cho gan MLII

# Giong het data/preprocess.py va backend/scripts/validate_classification.py
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


def evaluate_record(record_id, tol_ms=75, data_dir=DATA_DIR, channel=LEAD_II_CHANNEL):
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


if __name__ == "__main__":
    records = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_RECORDS

    ai_service.load_model("saved_models/resnet1d.pth")

    print("=" * 60)
    print("KIỂM CHỨNG NGOẠI SUY TRÊN DỮ LIỆU LẠ HOÀN TOÀN — INCART")
    print("(model chỉ train/val/test trên MIT-BIH, CHƯA từng thấy INCART)")
    print("=" * 60)

    all_true, all_pred = [], []
    print(f"{'Record':<8}{'N':>7}{'Accuracy':>12}{'F1(macro)':>12}")
    for rec in records:
        try:
            y_true, y_pred = evaluate_record(rec)
        except FileNotFoundError:
            print(f"[!] Bỏ qua {rec}: chưa tải — chạy backend/scripts/download_external_incart.py trước.")
            continue
        if len(y_true) == 0:
            print(f"[!] Bỏ qua {rec}: không khớp được nhịp GT nào trong ngưỡng thời gian.")
            continue
        acc = accuracy_score(y_true, y_pred)
        _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        print(f"{rec:<8}{len(y_true):>7}{acc*100:>11.2f}%{f1*100:>11.2f}%")
        all_true.extend(y_true.tolist())
        all_pred.extend(y_pred.tolist())

    if all_true:
        all_true = np.array(all_true)
        all_pred = np.array(all_pred)
        acc = accuracy_score(all_true, all_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(all_true, all_pred, average="macro", zero_division=0)
        print(f"\nTỔNG HỢP {len(records)} bản ghi INCART: n={len(all_true)} "
              f"Accuracy={acc*100:.2f}% Precision={prec*100:.2f}% Recall={rec*100:.2f}% F1={f1*100:.2f}%")
        print("Confusion matrix (hàng=thật, cột=dự đoán) [0=N,1=S,2=V,3=F,4=Q]:")
        print(confusion_matrix(all_true, all_pred, labels=[0, 1, 2, 3, 4]))
        print("\nSo sánh: 96.62% trên 8 bản ghi MIT-BIH (cùng nguồn dữ liệu train/test) — "
              "xem docs/benchmark_results.md.")
    else:
        print("\n[!] Không có dữ liệu hợp lệ nào để đánh giá.")
