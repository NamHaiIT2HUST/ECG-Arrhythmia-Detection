"""
Kiem chung end-to-end: doc tin hieu THO tu PhysioNet -> loc nhieu -> phat hien dinh R
(Pan-Tompkins) -> cat nhip 125Hz (dem so 0/cat bot) -> chay ResNet1D -> doi chieu voi
nhan AAMI cua bac si (file .atr). Day la thuoc do quan trong nhat de biet pipeline
real-time (backend/service/data_streamer.py, backend/service/diagnosis_service.py) co
that su dung do chinh xac gan voi benchmark offline (docs/benchmark_results.md) hay khong.

Chay: python -m backend.scripts.validate_classification [record_id ...]
"""
import sys
import numpy as np
import wfdb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import compute_all_beats
from backend.service.inference_service import ai_service

DEFAULT_RECORDS = ['100', '208', '207', '213', '119', '234', '200', '203']

# Anh xa ky hieu annotation MIT-BIH -> 5 lop AAMI (giong het data/preprocess.py)
AAMI_CLASSES = {
    'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,
    'A': 1, 'a': 1, 'J': 1, 'S': 1,
    'V': 2, 'E': 2,
    'F': 3,
    '/': 4, 'f': 4, 'Q': 4,
}
IDX2LABEL = {
    0: 'BÌNH THƯỜNG',
    1: 'CẢNH BÁO: TRÊN THẤT (S)',
    2: 'CẢNH BÁO: NHỊP THẤT (V)',
    3: 'CẢNH BÁO: HỢP NHẤT (F)',
    4: 'CẢNH BÁO: CHƯA RÕ (Q)',
}
LABEL2IDX = {v: k for k, v in IDX2LABEL.items()}


def evaluate_record(record_id, tol_ms=75, data_dir='data/raw/physionet_mitdb'):
    path = f'{data_dir}/{record_id}'
    signals, fields = wfdb.rdsamp(path, channels=[0])
    fs = fields['fs']
    signal = signals.flatten()

    ann = wfdb.rdann(path, 'atr')
    gt_samples = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in AAMI_CLASSES])
    gt_labels = np.array([AAMI_CLASSES[sym] for sym in ann.symbol if sym in AAMI_CLASSES])

    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    beats = compute_all_beats(clean, fs=fs)

    tol = int(tol_ms / 1000 * fs)
    y_true, y_pred = [], []
    for r_idx, window in beats:
        diffs = np.abs(gt_samples - r_idx)
        j = int(np.argmin(diffs)) if len(diffs) else None
        if j is None or diffs[j] > tol:
            continue  # khong khop dinh GT nao trong nguong (da danh gia rieng o validate_qrs.py)
        pred_text, _heatmap, _latency, _confidence = ai_service.predict(window)
        y_true.append(gt_labels[j])
        y_pred.append(LABEL2IDX.get(pred_text, -1))

    return np.array(y_true), np.array(y_pred)


if __name__ == '__main__':
    records = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_RECORDS

    ai_service.load_model('saved_models/resnet1d.pth')

    all_true, all_pred = [], []
    print(f"{'Record':<8}{'N':>7}{'Accuracy':>12}{'F1(macro)':>12}")
    for rec in records:
        try:
            y_true, y_pred = evaluate_record(rec)
        except FileNotFoundError:
            print(f"[!] Bỏ qua {rec}: không tìm thấy dữ liệu trong data/raw/physionet_mitdb/")
            continue
        if len(y_true) == 0:
            continue
        acc = accuracy_score(y_true, y_pred)
        _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
        print(f"{rec:<8}{len(y_true):>7}{acc*100:>11.2f}%{f1*100:>11.2f}%")
        all_true.extend(y_true.tolist())
        all_pred.extend(y_pred.tolist())

    if all_true:
        all_true = np.array(all_true)
        all_pred = np.array(all_pred)
        acc = accuracy_score(all_true, all_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(all_true, all_pred, average='macro', zero_division=0)
        print(f"\nTỔNG HỢP {len(records)} bản ghi: n={len(all_true)} "
              f"Accuracy={acc*100:.2f}% Precision={prec*100:.2f}% Recall={rec*100:.2f}% F1={f1*100:.2f}%")
        print("Confusion matrix (hàng=thật, cột=dự đoán) [0=N,1=S,2=V,3=F,4=Q]:")
        print(confusion_matrix(all_true, all_pred, labels=[0, 1, 2, 3, 4]))
