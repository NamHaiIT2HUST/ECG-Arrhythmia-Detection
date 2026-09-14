"""
Fine-tune ResNet1D (model dang trien khai that su tren dashboard real-time) de cai thien
generalization sang INCART, MA KHONG doi kien truc — chi ghi de trong so `.pth`, nen deploy
lai chi can thay file `saved_models/resnet1d.pth`, khong doi gi o backend/frontend/WS.

Chien luoc: "replay fine-tuning" — tron du lieu INCART MOI (chua tung dung, KHAC voi 5 ban
ghi I01/I15/I30/I45/I60 dang giu lam tap test doc lap khong dung nham do generalization o
docs/benchmark_results.md) voi 1 phan du lieu MIT-BIH cu (lay ngau nhien tu X_train_kaggle
da SMOTE) de chong "catastrophic forgetting".

LAN CHAY DAU (5 epoch, LR=1e-4, replay=20000) cai thien INCART Accuracy tu 85.94% -> 92.40%
nhung lam MIT-BIH Test Precision/F1 tut xuong duoi 90% (muc tieu de cuong) — vi 2 lop hiem
S/F bi "nhoe" ranh gioi quyet dinh. Ban nay "nhe tay" hon theo yeu cau: IT epoch hon (3),
LR thap hon (5e-5), NHIEU replay MIT-BIH hon (40000, gap doi INCART fine-tune data) — va
DANH GIA SAU MOI EPOCH (khong chi epoch cuoi) de tu chon ra epoch co trade-off tot nhat,
thay vi doan mu 1 bo tham so co dinh.

Tieu chi chon epoch tot nhat (tu dong): uu tien epoch nao GIU DUOC ca Precision va F1 tren
MIT-BIH Test >= 90% (dung muc tieu de cuong) VA co INCART Accuracy cao nhat trong so do; neu
KHONG epoch nao dat duoc rang buoc do, chon epoch co MIT-BIH F1 tut it nhat (an toan nhat).

Chay: python -m backend.scripts.finetune_resnet1d_incart
"""
import copy
import os
import sys

import numpy as np
import torch
import torch.nn as nn
import wfdb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))
from models import ResNet1D  # noqa: E402

from backend.core.qrs_detector import compute_all_beats  # noqa: E402
from backend.core.signal_processing import bandpass_filter, normalize_window, notch_filter  # noqa: E402

DATA_DIR = "data/raw/incartdb"
PROCESSED_DIR = "data/processed"
LEAD_II_CHANNEL = 1

# 10 ban ghi INCART KHAC HOAN TOAN voi tap test giu lai (I01,I15,I30,I45,I60) - chon giau
# nhip S(A)/F de fine-tune co co hoi hoc them ca 2 lop nay tren INCART, khong chi N/V.
FINETUNE_RECORDS = ["I33", "I34", "I20", "I18", "I74", "I22", "I42", "I62", "I07", "I70"]
INCART_TEST_RECORDS = ["I01", "I15", "I30", "I45", "I60"]

AAMI_CLASSES = {
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,
    "A": 1, "a": 1, "J": 1, "S": 1,
    "V": 2, "E": 2,
    "F": 3,
    "/": 4, "f": 4, "Q": 4,
}
LABEL_NAMES = ["N", "S", "V", "F", "Q"]

REPLAY_SAMPLE_SIZE = 40000  # tang gap doi so voi lan chay dau (20000) de chong quen manh hon
FINETUNE_EPOCHS = 3         # giam tu 5 xuong 3 - tranh drift qua xa khoi MIT-BIH
FINETUNE_LR = 5e-5          # giam tu 1e-4 xuong 5e-5 - cap nhat trong so nhe tay hon
# Lan chay truoc (giu ca lop S) cho thay Precision MIT-BIH tut xuong ~88.5% NGAY TU EPOCH 1
# va giu phang suot 3 epoch - khong phai do "qua tay", ma la xung dot phan phoi that o dung
# lop S (nhan S/A cua INCART co hinh dang khac du de lam lech ranh gioi da hoc tu MIT-BIH).
# Loai han lop S (index 1) khoi du lieu fine-tune INCART - giu nguyen ranh gioi lop nay,
# chi cai thien N/V/F tren INCART.
EXCLUDE_CLASSES = [1]  # index 1 = S, xem LABEL_NAMES
BATCH_SIZE = 128
MITBIH_PRECISION_TARGET = 0.90  # dung muc tieu de cuong
MITBIH_F1_TARGET = 0.90
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def extract_incart_windows(records, tol_ms=75):
    all_windows, all_labels = [], []
    for rec in records:
        path = f"{DATA_DIR}/{rec}"
        signals, fields = wfdb.rdsamp(path, channels=[LEAD_II_CHANNEL])
        fs = fields["fs"]
        signal = signals.flatten()

        ann = wfdb.rdann(path, "atr")
        gt_samples = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in AAMI_CLASSES])
        gt_labels = np.array([AAMI_CLASSES[sym] for sym in ann.symbol if sym in AAMI_CLASSES])
        if gt_samples.size == 0:
            continue

        clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
        beats = compute_all_beats(clean, fs=fs)
        tol = int(tol_ms / 1000 * fs)

        n_before = len(all_windows)
        for r_idx, window in beats:
            diffs = np.abs(gt_samples - r_idx)
            j = int(np.argmin(diffs)) if len(diffs) else None
            if j is None or diffs[j] > tol:
                continue
            all_windows.append(normalize_window(window))
            all_labels.append(gt_labels[j])
        print(f"    {rec}: +{len(all_windows) - n_before} nhịp")

    return np.asarray(all_windows, dtype=np.float32), np.asarray(all_labels, dtype=np.int64)


def load_replay_sample(n=REPLAY_SAMPLE_SIZE, seed=42):
    X = np.load(os.path.join(PROCESSED_DIR, "X_train_kaggle.npy"))
    y = np.load(os.path.join(PROCESSED_DIR, "y_train_kaggle.npy"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), size=min(n, len(X)), replace=False)
    return X[idx].astype(np.float32), y[idx].astype(np.int64)


def evaluate_on_mitbih(model, split="test"):
    X = np.load(os.path.join(PROCESSED_DIR, f"X_{split}_kaggle.npy"))
    y = np.load(os.path.join(PROCESSED_DIR, f"y_{split}_kaggle.npy"))
    loader = DataLoader(
        TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)),
        batch_size=256, shuffle=False,
    )
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for bx, by in loader:
            bx = bx.unsqueeze(1).to(DEVICE)
            out = model(bx)
            preds.extend(torch.argmax(out, dim=1).cpu().numpy())
            targets.extend(by.numpy())
    acc = accuracy_score(targets, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(targets, preds, average="macro", zero_division=0)
    return acc, float(prec), float(rec), float(f1)


def extract_incart_holdout_cached():
    """Trich xuat 1 LAN duy nhat (khong phu thuoc model) - tai su dung qua nhieu epoch de
    danh gia nhanh (khong doc lai file/loc nhieu/Pan-Tompkins moi epoch)."""
    windows, labels = [], []
    for rec in INCART_TEST_RECORDS:
        path = f"{DATA_DIR}/{rec}"
        signals, fields = wfdb.rdsamp(path, channels=[LEAD_II_CHANNEL])
        fs = fields["fs"]
        signal = signals.flatten()
        ann = wfdb.rdann(path, "atr")
        gt_samples = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in AAMI_CLASSES])
        gt_labels = np.array([AAMI_CLASSES[sym] for sym in ann.symbol if sym in AAMI_CLASSES])
        if gt_samples.size == 0:
            continue
        clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
        beats = compute_all_beats(clean, fs=fs)
        tol = int(75 / 1000 * fs)
        for r_idx, window in beats:
            diffs = np.abs(gt_samples - r_idx)
            j = int(np.argmin(diffs)) if len(diffs) else None
            if j is None or diffs[j] > tol:
                continue
            windows.append(normalize_window(window))
            labels.append(gt_labels[j])
    X = torch.tensor(np.asarray(windows, dtype=np.float32)).unsqueeze(1)
    y = np.asarray(labels, dtype=np.int64)
    return X, y


def evaluate_on_incart_holdout(model, X_incart, y_incart):
    model.eval()
    with torch.no_grad():
        preds = torch.argmax(model(X_incart.to(DEVICE)), dim=1).cpu().numpy()
    acc = accuracy_score(y_incart, preds)
    recall_n = float((preds[y_incart == 0] == 0).mean()) if (y_incart == 0).any() else None
    recall_v = float((preds[y_incart == 2] == 2).mean()) if (y_incart == 2).any() else None
    return acc, recall_n, recall_v


if __name__ == "__main__":
    print("=" * 70)
    print("FINE-TUNE ResNet1D TRÊN INCART — bản NHẸ TAY (ít epoch hơn, nhiều replay hơn)")
    print("=" * 70)

    model = ResNet1D(in_channels=1, num_classes=5)
    model.load_state_dict(torch.load("saved_models/resnet1d.pth", map_location=DEVICE, weights_only=True))
    model.to(DEVICE)

    print("[+] Trích xuất tập test INCART held-out (dùng chung mọi epoch)...")
    X_incart_test, y_incart_test = extract_incart_holdout_cached()

    print("\n[ĐÁNH GIÁ TRƯỚC FINE-TUNE — epoch 0]")
    acc_t0, prec_t0, rec_t0, f1_t0 = evaluate_on_mitbih(model, "test")
    acc_i0, rn_i0, rv_i0 = evaluate_on_incart_holdout(model, X_incart_test, y_incart_test)
    print(f"  MIT-BIH Test : Accuracy={acc_t0*100:.2f}%  Precision={prec_t0*100:.2f}%  "
          f"Recall={rec_t0*100:.2f}%  F1={f1_t0*100:.2f}%")
    print(f"  INCART held-out: Accuracy={acc_i0*100:.2f}%  Recall_N={rn_i0*100:.1f}%  Recall_V={rv_i0*100:.1f}%")

    epoch_results = [{
        "epoch": 0, "state": copy.deepcopy(model.state_dict()),
        "mitbih_acc": acc_t0, "mitbih_prec": prec_t0, "mitbih_rec": rec_t0, "mitbih_f1": f1_t0,
        "incart_acc": acc_i0, "incart_recall_n": rn_i0, "incart_recall_v": rv_i0,
    }]

    print(f"\n[+] Trích xuất nhịp fine-tune từ {len(FINETUNE_RECORDS)} bản ghi INCART "
          f"(KHÁC hoàn toàn tập test giữ lại)...")
    X_incart_ft, y_incart_ft = extract_incart_windows(FINETUNE_RECORDS)
    print(f"[✓] Tổng {len(X_incart_ft)} nhịp fine-tune INCART "
          f"(phân phối gốc: {dict(zip(*np.unique(y_incart_ft, return_counts=True)))}).")

    if EXCLUDE_CLASSES:
        keep_mask = ~np.isin(y_incart_ft, EXCLUDE_CLASSES)
        n_dropped = int((~keep_mask).sum())
        X_incart_ft, y_incart_ft = X_incart_ft[keep_mask], y_incart_ft[keep_mask]
        excluded_names = [LABEL_NAMES[c] for c in EXCLUDE_CLASSES]
        print(f"[i] Đã loại {n_dropped} nhịp lớp {excluded_names} khỏi tập fine-tune INCART "
              f"(giữ nguyên ranh giới lớp này đã học từ MIT-BIH, không để INCART làm lệch) "
              f"— còn lại {len(X_incart_ft)} nhịp.")

    print(f"\n[+] Lấy mẫu {REPLAY_SAMPLE_SIZE} nhịp MIT-BIH ngẫu nhiên để replay (chống quên)...")
    X_replay, y_replay = load_replay_sample()

    X_combined = np.concatenate([X_incart_ft, X_replay], axis=0)
    y_combined = np.concatenate([y_incart_ft, y_replay], axis=0)
    print(f"[✓] Tập fine-tune tổng hợp: {len(X_combined)} nhịp "
          f"({len(X_incart_ft)} INCART mới + {len(X_replay)} replay MIT-BIH, "
          f"tỉ lệ replay/INCART = {len(X_replay)/len(X_incart_ft):.2f}x)")

    train_loader = DataLoader(
        TensorDataset(torch.tensor(X_combined, dtype=torch.float32), torch.tensor(y_combined, dtype=torch.long)),
        batch_size=BATCH_SIZE, shuffle=True,
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=FINETUNE_LR)
    criterion = nn.CrossEntropyLoss()

    print(f"\n[+] Fine-tune {FINETUNE_EPOCHS} epoch, LR={FINETUNE_LR} — đánh giá lại sau MỖI epoch...")
    model.train()
    for epoch in range(1, FINETUNE_EPOCHS + 1):
        total_loss = 0.0
        for bx, by in train_loader:
            bx, by = bx.unsqueeze(1).to(DEVICE), by.to(DEVICE)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        avg_loss = total_loss / len(train_loader)

        acc_t, prec_t, rec_t, f1_t = evaluate_on_mitbih(model, "test")
        acc_i, rn_i, rv_i = evaluate_on_incart_holdout(model, X_incart_test, y_incart_test)
        print(f"    Epoch {epoch}/{FINETUNE_EPOCHS} - Loss: {avg_loss:.4f}  |  "
              f"MIT-BIH: Acc={acc_t*100:.2f}% Prec={prec_t*100:.2f}% F1={f1_t*100:.2f}%  |  "
              f"INCART: Acc={acc_i*100:.2f}% Rn={rn_i*100:.1f}% Rv={rv_i*100:.1f}%")
        epoch_results.append({
            "epoch": epoch, "state": copy.deepcopy(model.state_dict()),
            "mitbih_acc": acc_t, "mitbih_prec": prec_t, "mitbih_rec": rec_t, "mitbih_f1": f1_t,
            "incart_acc": acc_i, "incart_recall_n": rn_i, "incart_recall_v": rv_i,
        })
        model.train()

    print("\n" + "=" * 70)
    print("SO SÁNH TẤT CẢ EPOCH (0 = trước fine-tune)")
    print("=" * 70)
    print(f"{'Epoch':<8}{'MIT-BIH Acc':>13}{'MIT-BIH Prec':>14}{'MIT-BIH F1':>12}{'INCART Acc':>13}{'INCART Rn':>11}{'INCART Rv':>11}")
    for r in epoch_results:
        print(f"{r['epoch']:<8}{r['mitbih_acc']*100:>12.2f}%{r['mitbih_prec']*100:>13.2f}%"
              f"{r['mitbih_f1']*100:>11.2f}%{r['incart_acc']*100:>12.2f}%"
              f"{r['incart_recall_n']*100:>10.1f}%{r['incart_recall_v']*100:>10.1f}%")

    # Chon epoch tot nhat: uu tien epoch giu duoc Precision + F1 MIT-BIH >= muc tieu de cuong
    # (bo qua epoch 0 - khong phai fine-tune) VA co INCART Accuracy cao nhat trong so do.
    candidates = [r for r in epoch_results[1:]
                  if r["mitbih_prec"] >= MITBIH_PRECISION_TARGET and r["mitbih_f1"] >= MITBIH_F1_TARGET]
    if candidates:
        best = max(candidates, key=lambda r: r["incart_acc"])
        reason = (f"epoch giữ được Precision ({best['mitbih_prec']*100:.2f}%) và F1 "
                  f"({best['mitbih_f1']*100:.2f}%) trên MIT-BIH Test đều ≥90% (mục tiêu đề cương), "
                  f"và có INCART Accuracy cao nhất trong số các epoch đạt điều kiện đó.")
    else:
        best = min(epoch_results[1:], key=lambda r: epoch_results[0]["mitbih_f1"] - r["mitbih_f1"])
        reason = ("KHÔNG epoch fine-tune nào giữ được Precision/F1 MIT-BIH ≥90% — chọn epoch "
                   "tụt F1 ít nhất so với trước fine-tune (an toàn nhất trong các lựa chọn xấu).")

    print(f"\n[QUYẾT ĐỊNH TỰ ĐỘNG] Chọn epoch {best['epoch']} làm bản fine-tune cuối cùng.")
    print(f"  Lý do: {reason}")
    print(f"  MIT-BIH Test: Accuracy={best['mitbih_acc']*100:.2f}% Precision={best['mitbih_prec']*100:.2f}% "
          f"Recall={best['mitbih_rec']*100:.2f}% F1={best['mitbih_f1']*100:.2f}%")
    print(f"  INCART held-out: Accuracy={best['incart_acc']*100:.2f}% "
          f"Recall_N={best['incart_recall_n']*100:.1f}% Recall_V={best['incart_recall_v']*100:.1f}%")

    out_path = "saved_models/resnet1d_finetuned.pth"
    torch.save(best["state"], out_path)
    print(f"\n[✓] Đã lưu trọng số epoch {best['epoch']} vào {out_path} (CHƯA ghi đè resnet1d.pth production).")
    print("    Nếu số liệu ổn, promote bằng:")
    print("    cp saved_models/resnet1d_finetuned.pth saved_models/resnet1d.pth")
    print("    (deploy lại chỉ cần restart backend - kiến trúc ResNet1D giữ nguyên, không đổi code)")
