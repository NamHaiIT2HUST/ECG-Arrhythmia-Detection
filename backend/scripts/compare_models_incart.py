"""
Doi sanh CA 5 kien truc (khong chi ResNet1D) tren du lieu INCART - de tra loi cau hoi: co
model nao trong 5 model da benchmark generalize tot hon ResNet1D khi ra khoi phan phoi
MIT-BIH hay khong? Tai su dung dung logic trich xuat nhip (Pan-Tompkins + resample 125Hz)
cua validate_external_incart.py, nhung chi trich xuat 1 lan roi chay qua ca 5 kien truc
(thay vi goi lai ai_service - vi ai_service.load_model() chi ho tro rieng ResNet1D +
Grad-CAM gan cung vao layer3 cua no).

Yeu cau: da tai du lieu INCART truoc (backend/scripts/download_external_incart.py) va da co
du 5 file trong saved_models/ (cnn1d_lstm.pth, tcn.pth, resnet1d.pth, transformer1d.pth,
mamba1d.pth) - deu da co san tu buoc benchmark 5 model ban dau, khong can train lai.

Chay: python -m backend.scripts.compare_models_incart
"""
import os
import sys

import numpy as np
import torch
import wfdb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from models import CNN1D_LSTM, Mamba1D, ResNet1D, TemporalConvNet, Transformer1D  # noqa: E402

from backend.core.qrs_detector import compute_all_beats  # noqa: E402
from backend.core.signal_processing import bandpass_filter, normalize_window, notch_filter  # noqa: E402

DEFAULT_RECORDS = ["I01", "I15", "I30", "I45", "I60"]
DATA_DIR = "data/raw/incartdb"
LEAD_II_CHANNEL = 1

AAMI_CLASSES = {
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,
    "A": 1, "a": 1, "J": 1, "S": 1,
    "V": 2, "E": 2,
    "F": 3,
    "/": 4, "f": 4, "Q": 4,
}
LABEL_NAMES = ["N", "S", "V", "F", "Q"]

MODEL_REGISTRY = {
    "CNN1D_LSTM": (CNN1D_LSTM, "cnn1d_lstm.pth"),
    "TCN": (TemporalConvNet, "tcn.pth"),
    "ResNet1D": (ResNet1D, "resnet1d.pth"),
    "Transformer1D": (Transformer1D, "transformer1d.pth"),
    "Mamba1D": (Mamba1D, "mamba1d.pth"),
}

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def extract_incart_beats(records, data_dir=DATA_DIR, channel=LEAD_II_CHANNEL, tol_ms=75):
    """Trich xuat 1 lan (khong phu thuoc kien truc): tra ve list windows (187 diem, DA
    normalize_window) + nhan AAMI that tuong ung, gop tu tat ca record."""
    all_windows, all_labels, per_record_slice = [], [], {}

    for rec in records:
        path = f"{data_dir}/{rec}"
        signals, fields = wfdb.rdsamp(path, channels=[channel])
        fs = fields["fs"]
        signal = signals.flatten()

        ann = wfdb.rdann(path, "atr")
        gt_samples = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in AAMI_CLASSES])
        gt_labels = np.array([AAMI_CLASSES[sym] for sym in ann.symbol if sym in AAMI_CLASSES])
        if gt_samples.size == 0:
            per_record_slice[rec] = (len(all_windows), len(all_windows))
            continue

        clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
        beats = compute_all_beats(clean, fs=fs)

        tol = int(tol_ms / 1000 * fs)
        start = len(all_windows)
        for r_idx, window in beats:
            diffs = np.abs(gt_samples - r_idx)
            j = int(np.argmin(diffs)) if len(diffs) else None
            if j is None or diffs[j] > tol:
                continue
            all_windows.append(normalize_window(window))
            all_labels.append(gt_labels[j])
        per_record_slice[rec] = (start, len(all_windows))

    return np.asarray(all_windows, dtype=np.float32), np.asarray(all_labels, dtype=np.int64), per_record_slice


def run_model(model_class, weight_path, X):
    model = model_class()
    model.load_state_dict(torch.load(weight_path, map_location=DEVICE, weights_only=True))
    model.to(DEVICE)
    model.eval()

    preds = []
    with torch.no_grad():
        batch_size = 256
        for i in range(0, len(X), batch_size):
            batch = torch.tensor(X[i:i + batch_size]).unsqueeze(1).to(DEVICE)  # (B, 1, 187)
            out = model(batch)
            preds.extend(torch.argmax(out, dim=1).cpu().numpy().tolist())
    return np.asarray(preds, dtype=np.int64)


def recall_for_class(y_true, y_pred, cls):
    mask = y_true == cls
    if not mask.any():
        return None
    return float((y_pred[mask] == cls).mean())


if __name__ == "__main__":
    records = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_RECORDS

    print("=" * 70)
    print("ĐỐI SÁNH 5 KIẾN TRÚC TRÊN DỮ LIỆU LẠ HOÀN TOÀN (INCART, chưa từng thấy)")
    print("=" * 70)
    print("[+] Đang trích xuất nhịp từ INCART (dùng chung cho cả 5 model)...")
    X, y_true, per_record = extract_incart_beats(records)
    print(f"[✓] Tổng {len(X)} nhịp khớp GT trong ngưỡng thời gian, từ {len(records)} bản ghi.")

    present_classes = sorted(set(y_true.tolist()))
    print(f"[i] Lớp thật có mặt trong mẫu này: {[LABEL_NAMES[c] for c in present_classes]}")

    rows = []
    for name, (model_class, weight_file) in MODEL_REGISTRY.items():
        weight_path = os.path.join("saved_models", weight_file)
        if not os.path.exists(weight_path):
            print(f"[!] Bỏ qua {name}: không tìm thấy {weight_path}")
            continue
        y_pred = run_model(model_class, weight_path, X)
        acc = accuracy_score(y_true, y_pred)
        _, _, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=[0, 1, 2, 3, 4], average="macro", zero_division=0
        )
        recall_n = recall_for_class(y_true, y_pred, 0)
        recall_v = recall_for_class(y_true, y_pred, 2)
        rows.append((name, acc, f1_macro, recall_n, recall_v))
        print(f"    {name:<15} Accuracy={acc*100:6.2f}%  F1-macro*={f1_macro*100:6.2f}%  "
              f"Recall_N={'' if recall_n is None else f'{recall_n*100:.1f}%':>7}  "
              f"Recall_V={'' if recall_v is None else f'{recall_v*100:.1f}%':>7}")

    print("\n*F1-macro bị méo do lớp S/F/Q vắng mặt trong mẫu INCART này (xem "
          "docs/benchmark_results.md mục Generalization) — so sánh nên dựa vào Accuracy + "
          "Recall theo lớp N/V thực sự có mặt, không dựa F1-macro.")

    print("\n" + "=" * 70)
    print(f"{'Model':<15}{'Accuracy':>12}{'Recall N':>12}{'Recall V':>12}")
    for name, acc, f1_macro, recall_n, recall_v in sorted(rows, key=lambda r: -r[1]):
        rn = f"{recall_n*100:.1f}%" if recall_n is not None else "N/A"
        rv = f"{recall_v*100:.1f}%" if recall_v is not None else "N/A"
        print(f"{name:<15}{acc*100:>11.2f}%{rn:>12}{rv:>12}")
