"""
Kiem chung do chinh xac cua Pan-Tompkins R-peak detector (backend/core/qrs_detector.py)
bang cach doi chieu voi nhan bac si (physician annotation) co san trong file .atr cua
tung ban ghi MIT-BIH (cot chuan vang - ground truth).

Chay: python -m backend.scripts.validate_qrs [record_id ...]
Neu khong truyen record_id, mac dinh chay tren 1 bo ban ghi tieu bieu (de va kho).
"""
import sys
import numpy as np
import wfdb

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import pan_tompkins_r_peaks

DEFAULT_RECORDS = ['100', '208', '207', '213', '119', '234', '200', '203']
VALID_BEAT_SYMBOLS = set('NLRejAaJSVEFQ/f')  # chi tinh cac nhan la 1 nhip tim thuc su


def evaluate_record(record_id, tol_ms=75, data_dir='data/raw/physionet_mitdb'):
    path = f'{data_dir}/{record_id}'
    signals, fields = wfdb.rdsamp(path, channels=[0])
    fs = fields['fs']
    signal = signals.flatten()

    ann = wfdb.rdann(path, 'atr')
    gt = np.array([s for s, sym in zip(ann.sample, ann.symbol) if sym in VALID_BEAT_SYMBOLS])

    clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
    pred = pan_tompkins_r_peaks(clean, fs=fs)

    tol = int(tol_ms / 1000 * fs)
    matched_gt = np.zeros(len(gt), dtype=bool)
    tp = 0
    for p in pred:
        diffs = np.abs(gt - p)
        idx = int(np.argmin(diffs)) if len(diffs) else None
        if idx is not None and diffs[idx] <= tol and not matched_gt[idx]:
            matched_gt[idx] = True
            tp += 1

    fp = len(pred) - tp
    fn = len(gt) - tp
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        'record': record_id, 'gt': len(gt), 'pred': len(pred),
        'tp': tp, 'fp': fp, 'fn': fn,
        'precision': precision, 'recall': recall, 'f1': f1,
    }


if __name__ == '__main__':
    records = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_RECORDS

    print(f"{'Record':<8}{'GT':>6}{'Pred':>6}{'TP':>6}{'FP':>6}{'FN':>6}{'Precision':>12}{'Recall':>10}{'F1':>10}")
    f1_scores = []
    for rec in records:
        try:
            r = evaluate_record(rec)
        except FileNotFoundError:
            print(f"[!] Bo qua {rec}: khong tim thay du lieu trong data/raw/physionet_mitdb/")
            continue
        f1_scores.append(r['f1'])
        print(f"{r['record']:<8}{r['gt']:>6}{r['pred']:>6}{r['tp']:>6}{r['fp']:>6}{r['fn']:>6}"
              f"{r['precision']*100:>11.2f}%{r['recall']*100:>9.2f}%{r['f1']*100:>9.2f}%")

    if f1_scores:
        print(f"\nF1 trung binh tren {len(f1_scores)} ban ghi: {np.mean(f1_scores)*100:.2f}%")
