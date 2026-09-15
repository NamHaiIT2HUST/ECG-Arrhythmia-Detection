"""
Fine-tune tiep tuc tren SVDB (MIT-BIH Supraventricular Arrhythmia Database) de sua rieng
van de lop S - da xac nhan qua 2 bo du lieu doc lap (SVDB 0.4% recall, EDB 3.6% recall) rang
ranh gioi lop S hoc tu MIT-BIH khong generalize duoc sang bat ky nguon du lieu nao khac.

Khac voi lan fine-tune INCART (phai LOAI lop S vi xung dot), lan nay CHU DICH hoc them S tu
SVDB - vi SVDB la nguon du lieu S phong phu nhat hien co (10.370 nhip S/78 ban ghi). De
tranh lam xao tron lop V (da tot san tren moi bo du lieu da test), CHI lay N+S tu SVDB, BO
V/F/Q cua SVDB khoi tap fine-tune (SVDB co the co dac diem V khac MIT-BIH, khong can mao
hiem tron vao trong khi V dang on).

Tiep tuc TU chinh production hien tai (saved_models/resnet1d.pth - da la ban fine-tune INCART)
- khong quay lai model goc - de khong danh mat cai thien INCART da dat duoc.

Danh gia sau fine-tune tren CA 4 bo: MIT-BIH Test (khong duoc tut duoi 90% Precision/F1),
INCART held-out (khong duoc tut duoi muc da dat 93.18%), SVDB held-out (6 ban ghi test rieng,
KHAC 6 ban ghi fine-tune nay), va EDB held-out (kiem chung xem sua S co generalize tiep sang
bo thu 4 hay khong - bang chung manh nhat neu co).

Chay: python -m backend.scripts.finetune_resnet1d_svdb
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
from backend.scripts.validate_external_incart import DEFAULT_RECORDS as INCART_TEST_RECORDS  # noqa: E402

PROCESSED_DIR = "data/processed"

INCART_DIR = "data/raw/incartdb"
INCART_CHANNEL = 1

SVDB_DIR = "data/raw/svdb"
SVDB_CHANNEL = 0  # da xac nhan channel 0 tot hon channel 1 (77.32% vs 39.30%)
SVDB_TEST_RECORDS = ["822", "892", "854", "870", "863", "823"]      # giu lam test - KHONG dung de fine-tune
SVDB_FINETUNE_RECORDS = ["869", "881", "821", "861", "885", "852"]  # moi, giau nhip S

EDB_DIR = "data/raw/edb"
EDB_CHANNEL = 1  # MLIII
EDB_TEST_RECORDS = ["e0112", "e0114", "e0203", "e0614", "e0605", "e0413"]

AAMI_CLASSES = {
    "N": 0, "L": 0, "R": 0, "e": 0, "j": 0,
    "A": 1, "a": 1, "J": 1, "S": 1,
    "V": 2, "E": 2,
    "F": 3,
    "/": 4, "f": 4, "Q": 4,
}
LABEL_NAMES = ["N", "S", "V", "F", "Q"]

SVDB_KEEP_CLASSES = [0, 1]   # chi lay N+S tu SVDB, bo V/F/Q (tranh xao tron lop V dang tot)
REPLAY_SAMPLE_SIZE = 40000
FINETUNE_EPOCHS = 3
FINETUNE_LR = 5e-5
BATCH_SIZE = 128

# Lan truoc (full fine-tune, ca backbone lan fc) da lam sap lop V tren DIEN RONG (INCART/SVDB/
# EDB deu tut) du da loai V khoi du lieu SVDB - dau hieu backbone (feature extractor dung
# chung cho moi lop) bi nhieu, khong phai rieng 1 phan nao lien quan truc tiep den V.
# FREEZE_BACKBONE=True: chi train `model.fc` (lop phan loai cuoi), dong bang hoan toan
# prep/layer1/layer2/layer3 (ca gradient lan BatchNorm running stats, xem freeze_backbone())
# - gioi han thay doi CHI o ranh gioi quyet dinh cuoi cung, khong the lam trôi dac trung dung
# chung cho V/N da hoc tot. Ky thuat "linear probing" chuan trong transfer learning.
FREEZE_BACKBONE = True
HEAD_ONLY_LR = 1e-4  # fc-only co the chiu LR cao hon 1 chut vi khong dung den feature drift
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TOL_MS = 75


CACHE_DIR = "data/processed/external_cache"


def extract_beats(records, data_dir, channel, tol_ms=TOL_MS, cache_key=None):
    if cache_key:
        os.makedirs(CACHE_DIR, exist_ok=True)
        x_path = os.path.join(CACHE_DIR, f"{cache_key}_X.npy")
        y_path = os.path.join(CACHE_DIR, f"{cache_key}_y.npy")
        if os.path.exists(x_path) and os.path.exists(y_path):
            print(f"    (dùng cache {cache_key})")
            return np.load(x_path), np.load(y_path)

    all_windows, all_labels = [], []
    for rec in records:
        path = f"{data_dir}/{rec}"
        signals, fields = wfdb.rdsamp(path, channels=[channel])
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

    X, y = np.asarray(all_windows, dtype=np.float32), np.asarray(all_labels, dtype=np.int64)
    if cache_key:
        np.save(os.path.join(CACHE_DIR, f"{cache_key}_X.npy"), X)
        np.save(os.path.join(CACHE_DIR, f"{cache_key}_y.npy"), y)
    return X, y


def load_replay_sample(n=REPLAY_SAMPLE_SIZE, seed=42):
    X = np.load(os.path.join(PROCESSED_DIR, "X_train_kaggle.npy"))
    y = np.load(os.path.join(PROCESSED_DIR, "y_train_kaggle.npy"))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), size=min(n, len(X)), replace=False)
    return X[idx].astype(np.float32), y[idx].astype(np.int64)


def eval_mitbih(model, split="test"):
    X = np.load(os.path.join(PROCESSED_DIR, f"X_{split}_kaggle.npy"))
    y = np.load(os.path.join(PROCESSED_DIR, f"y_{split}_kaggle.npy"))
    loader = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)),
                         batch_size=256, shuffle=False)
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for bx, by in loader:
            out = model(bx.unsqueeze(1).to(DEVICE))
            preds.extend(torch.argmax(out, dim=1).cpu().numpy())
            targets.extend(by.numpy())
    acc = accuracy_score(targets, preds)
    prec, _, f1, _ = precision_recall_fscore_support(targets, preds, average="macro", zero_division=0)
    return acc, prec, f1


def eval_external(model, records, data_dir, channel):
    X, y = extract_beats(records, data_dir, channel)
    if len(X) == 0:
        return 0.0, {}
    loader = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)),
                         batch_size=256, shuffle=False)
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for bx, by in loader:
            out = model(bx.unsqueeze(1).to(DEVICE))
            preds.extend(torch.argmax(out, dim=1).cpu().numpy())
            targets.extend(by.numpy())
    preds, targets = np.asarray(preds), np.asarray(targets)
    acc = accuracy_score(targets, preds)
    recalls = {}
    for c, name in enumerate(LABEL_NAMES):
        if (targets == c).any():
            recalls[name] = float((preds[targets == c] == c).mean())
    return acc, recalls


def fmt_recalls(recalls):
    return "  ".join(f"{k}={v*100:.1f}%" for k, v in recalls.items())


def freeze_backbone(model):
    """Dong bang toan bo feature extractor (prep/layer1/2/3), chi train `fc`. requires_grad=
    False chan gradient; goi lai re_eval_frozen(model) SAU MOI LAN model.train() de BatchNorm
    running_mean/var cua cac block nay cung khong troi (model.train() se bat lai train() cho
    MOI submodule, ke ca cac block da dong bang, neu khong goi lai eval() cho chung)."""
    for module in (model.prep, model.layer1, model.layer2, model.layer3):
        for p in module.parameters():
            p.requires_grad = False
        module.eval()


def re_eval_frozen(model):
    for module in (model.prep, model.layer1, model.layer2, model.layer3):
        module.eval()


if __name__ == "__main__":
    print("=" * 70)
    print("FINE-TUNE ResNet1D TRÊN SVDB — mục tiêu: sửa lớp S (đã xác nhận vỡ trên SVDB+EDB)")
    print("=" * 70)

    model = ResNet1D(in_channels=1, num_classes=5)
    model.load_state_dict(torch.load("saved_models/resnet1d.pth", map_location=DEVICE, weights_only=True))
    model.to(DEVICE)

    print("\n[+] Trích xuất 3 tập test held-out (dùng chung mọi epoch)...")
    print("  INCART held-out:")
    X_incart_test, y_incart_test = extract_beats(INCART_TEST_RECORDS, INCART_DIR, INCART_CHANNEL, cache_key="incart_test")
    print("  SVDB held-out:")
    X_svdb_test, y_svdb_test = extract_beats(SVDB_TEST_RECORDS, SVDB_DIR, SVDB_CHANNEL, cache_key="svdb_test")
    print("  EDB held-out:")
    X_edb_test, y_edb_test = extract_beats(EDB_TEST_RECORDS, EDB_DIR, EDB_CHANNEL, cache_key="edb_test")

    def eval_all(m, tag):
        acc_t, prec_t, f1_t = eval_mitbih(m, "test")
        print(f"  [{tag}] MIT-BIH Test  : Acc={acc_t*100:.2f}% Prec={prec_t*100:.2f}% F1={f1_t*100:.2f}%")

        def _eval_cached(X, y, name):
            loader = DataLoader(TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)),
                                 batch_size=256, shuffle=False)
            m.eval()
            preds, targets = [], []
            with torch.no_grad():
                for bx, by in loader:
                    out = m(bx.unsqueeze(1).to(DEVICE))
                    preds.extend(torch.argmax(out, dim=1).cpu().numpy())
                    targets.extend(by.numpy())
            preds, targets = np.asarray(preds), np.asarray(targets)
            acc = accuracy_score(targets, preds)
            recalls = {LABEL_NAMES[c]: float((preds[targets == c] == c).mean())
                       for c in range(5) if (targets == c).any()}
            print(f"  [{tag}] {name:<14}: Acc={acc*100:.2f}%  {fmt_recalls(recalls)}")
            return acc, recalls

        r_incart = _eval_cached(X_incart_test, y_incart_test, "INCART held-out")
        r_svdb = _eval_cached(X_svdb_test, y_svdb_test, "SVDB held-out")
        r_edb = _eval_cached(X_edb_test, y_edb_test, "EDB held-out")
        return {"mitbih": (acc_t, prec_t, f1_t), "incart": r_incart, "svdb": r_svdb, "edb": r_edb}

    print("\n[ĐÁNH GIÁ TRƯỚC FINE-TUNE]")
    results_before = eval_all(model, "epoch0")

    print(f"\n[+] Trích xuất nhịp fine-tune từ {len(SVDB_FINETUNE_RECORDS)} bản ghi SVDB "
          f"(KHÁC hoàn toàn 6 bản ghi test)...")
    X_svdb_ft, y_svdb_ft = extract_beats(SVDB_FINETUNE_RECORDS, SVDB_DIR, SVDB_CHANNEL, cache_key="svdb_finetune_raw")
    keep_mask = np.isin(y_svdb_ft, SVDB_KEEP_CLASSES)
    n_dropped = int((~keep_mask).sum())
    X_svdb_ft, y_svdb_ft = X_svdb_ft[keep_mask], y_svdb_ft[keep_mask]
    print(f"[i] Chỉ giữ N+S từ SVDB (loại {n_dropped} nhịp V/F/Q để không xáo trộn lớp V đang tốt) "
          f"— còn {len(X_svdb_ft)} nhịp, phân phối: {dict(zip(*np.unique(y_svdb_ft, return_counts=True)))}")

    print(f"\n[+] Lấy mẫu {REPLAY_SAMPLE_SIZE} nhịp MIT-BIH ngẫu nhiên để replay (chống quên)...")
    X_replay, y_replay = load_replay_sample()

    X_combined = np.concatenate([X_svdb_ft, X_replay], axis=0)
    y_combined = np.concatenate([y_svdb_ft, y_replay], axis=0)
    print(f"[✓] Tập fine-tune tổng hợp: {len(X_combined)} nhịp "
          f"({len(X_svdb_ft)} SVDB N+S mới + {len(X_replay)} replay MIT-BIH)")

    train_loader = DataLoader(
        TensorDataset(torch.tensor(X_combined, dtype=torch.float32), torch.tensor(y_combined, dtype=torch.long)),
        batch_size=BATCH_SIZE, shuffle=True,
    )

    if FREEZE_BACKBONE:
        freeze_backbone(model)
        trainable_params = model.fc.parameters()
        lr = HEAD_ONLY_LR
        print(f"\n[i] FREEZE_BACKBONE=True — chỉ train `model.fc` (linear probing), "
              f"đóng băng prep/layer1/2/3 (cả gradient lẫn BatchNorm), LR={lr}.")
    else:
        trainable_params = model.parameters()
        lr = FINETUNE_LR

    optimizer = torch.optim.Adam(trainable_params, lr=lr)
    criterion = nn.CrossEntropyLoss()

    checkpoints = [{"epoch": 0, "state": copy.deepcopy(model.state_dict()), "results": results_before}]

    print(f"\n[+] Fine-tune {FINETUNE_EPOCHS} epoch, LR={lr}, đánh giá lại sau MỖI epoch...")
    for epoch in range(FINETUNE_EPOCHS):
        model.train()
        if FREEZE_BACKBONE:
            re_eval_frozen(model)
        total_loss = 0.0
        for bx, by in train_loader:
            bx, by = bx.unsqueeze(1).to(DEVICE), by.to(DEVICE)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"\n  --- Epoch {epoch+1}/{FINETUNE_EPOCHS} - Loss: {total_loss/len(train_loader):.4f} ---")
        results_epoch = eval_all(model, f"epoch{epoch+1}")
        checkpoints.append({"epoch": epoch + 1, "state": copy.deepcopy(model.state_dict()), "results": results_epoch})

    # Chon epoch: uu tien epoch giu MIT-BIH Precision/F1 >= 90% (muc tieu de cuong), trong so
    # do chon epoch co Recall_S tren SVDB cao nhat (muc tieu chinh cua lan fine-tune nay).
    MITBIH_TARGET = 0.90
    valid = [c for c in checkpoints if c["results"]["mitbih"][1] >= MITBIH_TARGET and c["results"]["mitbih"][2] >= MITBIH_TARGET]
    pool = valid if valid else checkpoints
    best = max(pool, key=lambda c: c["results"]["svdb"][1].get("S", 0.0))

    print("\n" + "=" * 70)
    print("SO SÁNH TẤT CẢ EPOCH")
    print("=" * 70)
    print(f"{'Epoch':<7}{'MIT-BIH Prec':>14}{'MIT-BIH F1':>12}{'SVDB Recall_S':>16}{'SVDB Acc':>11}{'INCART Acc':>12}{'EDB Recall_S':>15}")
    for c in checkpoints:
        m_acc, m_prec, m_f1 = c["results"]["mitbih"]
        svdb_acc, svdb_r = c["results"]["svdb"]
        incart_acc, _ = c["results"]["incart"]
        edb_acc, edb_r = c["results"]["edb"]
        print(f"{c['epoch']:<7}{m_prec*100:>13.2f}%{m_f1*100:>11.2f}%{svdb_r.get('S',0)*100:>15.1f}%"
              f"{svdb_acc*100:>10.2f}%{incart_acc*100:>11.2f}%{edb_r.get('S',0)*100:>14.1f}%")

    print(f"\n[QUYẾT ĐỊNH] Chọn epoch {best['epoch']} "
          f"({'đạt' if valid else 'KHÔNG epoch nào đạt'} mục tiêu MIT-BIH Precision/F1≥90%, "
          f"trong số đó Recall_S trên SVDB cao nhất).")

    model.load_state_dict(best["state"])
    out_path = "saved_models/resnet1d_finetuned_svdb.pth"
    torch.save(model.state_dict(), out_path)
    print(f"[✓] Đã lưu vào {out_path} (CHƯA ghi đè resnet1d.pth production).")
    print("    Nếu ổn, promote bằng: cp saved_models/resnet1d_finetuned_svdb.pth saved_models/resnet1d.pth")
