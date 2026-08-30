"""
CP6.1: Chuyển ResNet1D (model production, xem docs/benchmark_results.md) từ PyTorch sang ONNX,
kiểm chứng sai số so với PyTorch gốc, đo latency, và tạo thêm bản lượng hoá INT8.

Chạy: python -m src.models.export_onnx
"""
import os
import time

import numpy as np
import onnxruntime as ort
import torch
from onnxruntime.quantization import QuantType, quantize_dynamic

from src.models.resnet1d import ResNet1D

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")

PYTORCH_PATH = os.path.join(SAVED_MODELS_DIR, "resnet1d.pth")
ONNX_FP32_PATH = os.path.join(SAVED_MODELS_DIR, "resnet1d.onnx")
ONNX_INT8_PATH = os.path.join(SAVED_MODELS_DIR, "resnet1d_int8.onnx")

INPUT_SHAPE = (1, 1, 187)  # (batch, channels, seq_len) - khớp ResNet1D.forward()


def load_pytorch_model():
    model = ResNet1D(in_channels=1, num_classes=5)
    model.load_state_dict(torch.load(PYTORCH_PATH, map_location="cpu", weights_only=True))
    model.eval()
    return model


def export_to_onnx(model, onnx_path=ONNX_FP32_PATH, opset_version=17):
    """Xuất ONNX với batch động (dynamic_axes) để dùng được cả cho batch=1 (real-time,
    inference_service.py) lẫn batch lớn (benchmark/offline diagnosis)."""
    dummy_input = torch.randn(*INPUT_SHAPE, dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch_size"}, "logits": {0: "batch_size"}},
        opset_version=opset_version,
        # PyTorch 2.x mặc định dùng exporter mới dựa trên "dynamo" (cần thêm package
        # onnxscript). Kiến trúc ResNet1D không có control-flow động nên dùng thẳng
        # exporter kiểu cũ (TorchScript-based) cho đơn giản, ổn định, không cần thêm dependency.
        dynamo=False,
    )
    print(f"[✓] Đã xuất ONNX (FP32): {onnx_path}")


def verify_parity(model, onnx_path=ONNX_FP32_PATH, n_samples=200, rtol=1e-3):
    """So sánh đầu ra PyTorch vs ONNX Runtime trên nhiều batch ngẫu nhiên khác nhau.

    LƯU Ý: bản đầu tiên dùng ngưỡng SAI SỐ TUYỆT ĐỐI 1e-5 trên logit thô (theo đề xuất ban
    đầu trong plan.md) — kiểm tra thực tế cho thấy sai số tuyệt đối lớn nhất là ~2.4e-4,
    vượt ngưỡng đó. Nhưng sai số TƯƠNG ĐỐI chỉ ~8e-7 (cực nhỏ, đúng như kỳ vọng của cộng trừ
    dấu phẩy động FP32) và trên 200 batch ngẫu nhiên, KHÔNG có batch nào bị đổi lớp dự đoán
    (argmax). Kết luận: 1e-5 tuyệt đối là ngưỡng sai — hợp lý cho 1 phép tính đơn lẻ, không
    hợp lý cho logit thô sau hàng chục lớp Conv/BatchNorm tích luỹ sai số của 2 backend toán
    học khác nhau (PyTorch dùng MKL/oneDNN, ONNX Runtime dùng kernel riêng). Tiêu chí đúng ở
    đây là (a) lớp dự đoán (argmax) phải khớp 100% — đây là điều THỰC SỰ ảnh hưởng tới hành
    vi model, và (b) sai số tương đối nhỏ để chắc chắn không có bug logic trong export.
    """
    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    max_abs_diff = 0.0
    max_rel_diff = 0.0
    argmax_mismatches = 0

    with torch.no_grad():
        for _ in range(n_samples):
            x = torch.randn(*INPUT_SHAPE, dtype=torch.float32)
            torch_out = model(x).numpy()
            onnx_out = session.run(None, {"input": x.numpy()})[0]

            abs_diff = np.abs(torch_out - onnx_out)
            max_abs_diff = max(max_abs_diff, float(abs_diff.max()))
            max_rel_diff = max(max_rel_diff, float((abs_diff / (np.abs(torch_out) + 1e-8)).max()))
            if int(np.argmax(torch_out, axis=1)[0]) != int(np.argmax(onnx_out, axis=1)[0]):
                argmax_mismatches += 1

    ok = argmax_mismatches == 0 and max_rel_diff < rtol
    print(f"[{'✓' if ok else '✗'}] PyTorch vs ONNX FP32 (n={n_samples} batch ngẫu nhiên): "
          f"lớp dự đoán khớp {n_samples - argmax_mismatches}/{n_samples}, "
          f"sai số tương đối lớn nhất {max_rel_diff:.2e} (ngưỡng {rtol:.0e}), "
          f"sai số tuyệt đối lớn nhất {max_abs_diff:.2e} (chỉ để tham khảo)")
    assert ok, (f"Argmax lệch {argmax_mismatches}/{n_samples} batch hoặc sai số tương đối "
                f"{max_rel_diff:.2e} vượt ngưỡng {rtol:.0e} — export ONNX có vấn đề thật.")
    return max_abs_diff, max_rel_diff


def quantize_to_int8(fp32_path=ONNX_FP32_PATH, int8_path=ONNX_INT8_PATH):
    quantize_dynamic(fp32_path, int8_path, weight_type=QuantType.QUInt8)
    print(f"[✓] Đã lượng hoá INT8: {int8_path}")


def benchmark_latency(model, onnx_path, n_runs=200, warmup=10):
    """Đo latency trung bình 1 mẫu (ms), so PyTorch FP32 vs 1 bản ONNX bất kỳ (FP32 hoặc INT8)."""
    x_torch = torch.randn(*INPUT_SHAPE, dtype=torch.float32)
    x_numpy = x_torch.numpy()

    session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    with torch.no_grad():
        for _ in range(warmup):
            model(x_torch)
    for _ in range(warmup):
        session.run(None, {"input": x_numpy})

    with torch.no_grad():
        t0 = time.perf_counter()
        for _ in range(n_runs):
            model(x_torch)
        torch_latency_ms = (time.perf_counter() - t0) / n_runs * 1000

    t0 = time.perf_counter()
    for _ in range(n_runs):
        session.run(None, {"input": x_numpy})
    onnx_latency_ms = (time.perf_counter() - t0) / n_runs * 1000

    return torch_latency_ms, onnx_latency_ms


def file_size_kb(path):
    return os.path.getsize(path) / 1024


if __name__ == "__main__":
    # LƯU Ý: script này CHỈ xuất + kiểm tra parity + đo size/latency thô — KHÔNG ghi
    # docs/onnx_comparison.md. Báo cáo đầy đủ (kèm accuracy end-to-end + phân tích) do
    # `backend/scripts/validate_onnx_classification.py` ghi, chạy SAU script này, vì
    # accuracy cần chạy qua toàn bộ pipeline DSP + nhãn bác sĩ (chậm hơn nhiều so với
    # export/latency). Ghi báo cáo ở đây rồi để script kia ghi đè lại từng là nguồn gây
    # mất nội dung: chạy lại mỗi mình export_onnx.py sẽ xoá mất phần accuracy/phân tích
    # đã có trong file — xem lịch sử phiên 2026-08-30.
    model = load_pytorch_model()

    export_to_onnx(model)
    verify_parity(model)
    quantize_to_int8()

    torch_latency, fp32_latency = benchmark_latency(model, ONNX_FP32_PATH)
    _, int8_latency = benchmark_latency(model, ONNX_INT8_PATH)

    pth_size = file_size_kb(PYTORCH_PATH)
    fp32_size = file_size_kb(ONNX_FP32_PATH)
    int8_size = file_size_kb(ONNX_INT8_PATH)

    print(f"\n[i] Kích thước : PyTorch={pth_size:.1f}KB | ONNX FP32={fp32_size:.1f}KB | ONNX INT8={int8_size:.1f}KB")
    print(f"[i] Latency    : PyTorch={torch_latency:.4f}ms | ONNX FP32={fp32_latency:.4f}ms | ONNX INT8={int8_latency:.4f}ms")
    print("\n[i] Chạy tiếp 'python -m backend.scripts.validate_onnx_classification' để đo "
          "accuracy end-to-end và ghi báo cáo đầy đủ vào docs/onnx_comparison.md.")
