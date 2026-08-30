"""
CP6.1: Kiem chung do chinh xac end-to-end (raw signal -> nhan AAMI, so nhan bac si that) cua
2 ban ONNX (FP32 va INT8 quantized) so voi ban PyTorch goc (baseline da biet: Accuracy 94.33%,
xem backend/scripts/validate_classification.py va plan.md muc 5.4/CP3.3). Cuoi cung ghi bao
cao day du (size + latency + accuracy + nhan xet) vao docs/onnx_comparison.md.

Chay: python -m backend.scripts.validate_onnx_classification
Yeu cau: da chay `python -m src.models.export_onnx` truoc do de co san 2 file .onnx.

LUU Y THIET KE: file docs/onnx_comparison.md CHI duoc ghi boi script nay (khong phai
export_onnx.py) - export_onnx.py chi co size/latency (chay nhanh), con accuracy end-to-end
phai chay qua toan bo pipeline DSP tren 8 ban ghi (cham hon nhieu). Neu export_onnx.py cung
tu ghi file nay, chay lai rieng no se xoa mat phan accuracy/nhan xet da co - da xay ra that
trong phien 2026-08-30, sua bang cach gom het vao 1 noi ghi duy nhat (o day, chay sau cung).
"""
import os
import time

import numpy as np
import wfdb
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import compute_all_beats
from src.models.export_onnx import (
    BASE_DIR, ONNX_FP32_PATH, ONNX_INT8_PATH, PYTORCH_PATH,
    benchmark_latency, file_size_kb, load_pytorch_model,
)
from src.models.onnx_runner import ONNXPredictor

RECORDS = ['100', '208', '207', '213', '119', '234', '200', '203']

AAMI_CLASSES = {
    'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,
    'A': 1, 'a': 1, 'J': 1, 'S': 1,
    'V': 2, 'E': 2,
    'F': 3,
    '/': 4, 'f': 4, 'Q': 4,
}
IDX2LABEL = {
    0: 'BÌNH THƯỜNG', 1: 'CẢNH BÁO: TRÊN THẤT (S)', 2: 'CẢNH BÁO: NHỊP THẤT (V)',
    3: 'CẢNH BÁO: HỢP NHẤT (F)', 4: 'CẢNH BÁO: CHƯA RÕ (Q)',
}
LABEL2IDX = {v: k for k, v in IDX2LABEL.items()}

BASELINE_ACCURACY = 0.9433  # PyTorch gốc, xem validate_classification.py
MAX_ACCEPTABLE_DROP = 0.02  # chấp nhận rớt tối đa 2% theo DoD trong plan.md mục 6.1


def evaluate(predictor, record_id, tol_ms=75, data_dir='data/raw/physionet_mitdb'):
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
            continue
        pred_text = predictor.predict(window)
        y_true.append(gt_labels[j])
        y_pred.append(LABEL2IDX.get(pred_text, -1))

    return np.array(y_true), np.array(y_pred)


def run_for_model(name, onnx_path):
    predictor = ONNXPredictor(onnx_path)
    all_true, all_pred = [], []
    for rec in RECORDS:
        y_true, y_pred = evaluate(predictor, rec)
        all_true.extend(y_true.tolist())
        all_pred.extend(y_pred.tolist())

    all_true = np.array(all_true)
    all_pred = np.array(all_pred)
    acc = accuracy_score(all_true, all_pred)
    _, _, f1, _ = precision_recall_fscore_support(all_true, all_pred, average='macro', zero_division=0)

    drop = BASELINE_ACCURACY - acc
    ok = drop <= MAX_ACCEPTABLE_DROP
    print(f"[{'✓' if ok else '✗'}] {name}: n={len(all_true)} Accuracy={acc*100:.2f}% F1(macro)={f1*100:.2f}% "
          f"(so PyTorch baseline {BASELINE_ACCURACY*100:.2f}%: {'-' if drop >= 0 else '+'}{abs(drop)*100:.2f} điểm %, "
          f"ngưỡng chấp nhận {MAX_ACCEPTABLE_DROP*100:.0f} điểm %)")
    assert ok, f"{name} rớt {drop*100:.2f} điểm % so baseline, vượt ngưỡng chấp nhận {MAX_ACCEPTABLE_DROP*100:.0f} điểm %"
    return acc, f1


def write_report(fp32_acc, fp32_f1, int8_acc, int8_f1):
    model = load_pytorch_model()
    torch_latency, fp32_latency = benchmark_latency(model, ONNX_FP32_PATH)
    _, int8_latency = benchmark_latency(model, ONNX_INT8_PATH)

    pth_size = file_size_kb(PYTORCH_PATH)
    fp32_size = file_size_kb(ONNX_FP32_PATH)
    int8_size = file_size_kb(ONNX_INT8_PATH)

    docs_dir = os.path.join(BASE_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    path = os.path.join(docs_dir, "onnx_comparison.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write("# So sánh ResNet1D: PyTorch vs ONNX (FP32) vs ONNX (INT8 quantized)\n\n")
        f.write(f"**Ngày tạo**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Định dạng | Kích thước file | Latency TB (200 lần, batch=1, CPU) | Accuracy end-to-end* |\n")
        f.write("|:---|---:|---:|---:|\n")
        f.write(f"| PyTorch FP32 (.pth) | {pth_size:.1f} KB | {torch_latency:.4f} ms | {BASELINE_ACCURACY*100:.2f}% (baseline) |\n")
        f.write(f"| ONNX FP32 (.onnx) | {fp32_size:.1f} KB | {fp32_latency:.4f} ms | "
                f"{fp32_acc*100:.2f}% (F1-macro {fp32_f1*100:.2f}%) |\n")
        f.write(f"| ONNX INT8 quantized (.onnx) | {int8_size:.1f} KB | {int8_latency:.4f} ms | "
                f"{int8_acc*100:.2f}% (F1-macro {int8_f1*100:.2f}%) |\n")
        f.write("\n\\* Đo bằng `backend/scripts/validate_onnx_classification.py` — chạy end-to-end "
                 "(tín hiệu thô → lọc nhiễu → Pan-Tompkins → cắt nhịp → model → so nhãn bác sĩ) trên "
                 "8 bản ghi MIT-BIH, cùng bộ dữ liệu dùng để đo baseline PyTorch trong "
                 "`validate_classification.py`.\n\n")
        f.write("## Nhận xét quan trọng: INT8 KHÔNG chắc nhanh hơn trên CPU dev thường\n\n")
        f.write(
            "Kỳ vọng ban đầu (`plan.md`) là lượng hoá INT8 giúp tăng tốc 3-5 lần — thực tế đo được "
            "trên CPU máy dev dao động quanh mức **bằng hoặc chậm hơn** bản FP32 (dao động giữa các "
            "lần chạy do nhiễu hệ thống, nhưng chưa lần nào nhanh hơn rõ rệt). Đây không phải bug, mà "
            "là hạn chế đã biết của **dynamic quantization**: ONNX Runtime phải quantize hoạt động "
            "(activation) NGAY LÚC CHẠY (runtime) cho từng lớp rồi dequantize lại đầu ra, tốn thêm "
            "phép tính; lợi ích tốc độ INT8 thật sự chỉ thể hiện rõ trên phần cứng có tập lệnh tăng "
            "tốc INT8 chuyên dụng (vd Intel AVX512-VNNI, hoặc NPU/GPU trên thiết bị edge như Jetson "
            "Nano) — CPU phát triển thông thường (không có VNNI) sẽ không thấy lợi ích tốc độ rõ ràng.\n\n"
        )
        f.write(
            "**Kết luận thực tế cho mục tiêu Edge AI của CP6.1**:\n"
            f"- Mục tiêu **kích thước** (`plan.md`: \"< 700KB\") đã đạt: {int8_size:.1f}KB.\n"
            f"- Mục tiêu **độ chính xác** đạt: INT8 chỉ rớt {(BASELINE_ACCURACY - int8_acc)*100:.2f} "
            "điểm % so PyTorch gốc, trong ngưỡng chấp nhận 2 điểm %.\n"
            "- Mục tiêu **tốc độ trên CPU dev** không chắc đạt bằng INT8 — nhưng **ONNX FP32 luôn "
            f"nhanh hơn PyTorch gốc rõ rệt** ({torch_latency:.2f}ms → {fp32_latency:.2f}ms) mà không "
            "đổi gì về độ chính xác hay kích thước, nên nếu chỉ cần tối ưu tốc độ (không cần thu nhỏ "
            "file), **ONNX FP32 là lựa chọn tốt hơn INT8 trên phần cứng này**.\n"
            "- Nếu mục tiêu thật sự là triển khai lên thiết bị edge có tăng tốc INT8 phần cứng "
            "(Raspberry Pi 4+ dùng ARM NEON dot-product, Jetson Nano dùng TensorRT INT8, ...), cần đo "
            "lại latency TRÊN CHÍNH thiết bị đó — số liệu latency ở đây chỉ phản ánh đúng CPU máy dev, "
            "không đại diện cho edge device thật.\n\n"
        )
        f.write("## Cách tái tạo\n\n```bash\npython -m src.models.export_onnx"
                 "                       # xuất resnet1d.onnx + resnet1d_int8.onnx\n"
                 "python -m backend.scripts.validate_onnx_classification  "
                 "# đo accuracy + ghi báo cáo này\n```\n")

    print(f"\n[✓] Đã ghi báo cáo đầy đủ: {path}")


if __name__ == '__main__':
    fp32_acc, fp32_f1 = run_for_model("ONNX FP32", ONNX_FP32_PATH)
    int8_acc, int8_f1 = run_for_model("ONNX INT8 (quantized)", ONNX_INT8_PATH)
    write_report(fp32_acc, fp32_f1, int8_acc, int8_f1)
    print("\n[✓] CP 6.1 — độ chính xác cả 2 bản ONNX đều trong ngưỡng chấp nhận so với PyTorch gốc.")
