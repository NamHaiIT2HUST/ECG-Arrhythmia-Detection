# So sánh ResNet1D: PyTorch vs ONNX (FP32) vs ONNX (INT8 quantized)

**Ngày tạo**: 2026-08-30 23:49:51

| Định dạng | Kích thước file | Latency TB (200 lần, batch=1, CPU) | Accuracy end-to-end* |
|:---|---:|---:|---:|
| PyTorch FP32 (.pth) | 2734.9 KB | 1.0817 ms | 94.33% (baseline) |
| ONNX FP32 (.onnx) | 2703.4 KB | 0.2691 ms | 94.33% (F1-macro 60.27%) |
| ONNX INT8 quantized (.onnx) | 697.3 KB | 1.0027 ms | 94.18% (F1-macro 59.97%) |

\* Đo bằng `backend/scripts/validate_onnx_classification.py` — chạy end-to-end (tín hiệu thô → lọc nhiễu → Pan-Tompkins → cắt nhịp → model → so nhãn bác sĩ) trên 8 bản ghi MIT-BIH, cùng bộ dữ liệu dùng để đo baseline PyTorch trong `validate_classification.py`.

## Nhận xét quan trọng: INT8 KHÔNG chắc nhanh hơn trên CPU dev thường

Kỳ vọng ban đầu (`plan.md`) là lượng hoá INT8 giúp tăng tốc 3-5 lần — thực tế đo được trên CPU máy dev dao động quanh mức **bằng hoặc chậm hơn** bản FP32 (dao động giữa các lần chạy do nhiễu hệ thống, nhưng chưa lần nào nhanh hơn rõ rệt). Đây không phải bug, mà là hạn chế đã biết của **dynamic quantization**: ONNX Runtime phải quantize hoạt động (activation) NGAY LÚC CHẠY (runtime) cho từng lớp rồi dequantize lại đầu ra, tốn thêm phép tính; lợi ích tốc độ INT8 thật sự chỉ thể hiện rõ trên phần cứng có tập lệnh tăng tốc INT8 chuyên dụng (vd Intel AVX512-VNNI, hoặc NPU/GPU trên thiết bị edge như Jetson Nano) — CPU phát triển thông thường (không có VNNI) sẽ không thấy lợi ích tốc độ rõ ràng.

**Kết luận thực tế cho mục tiêu Edge AI của CP6.1**:
- Mục tiêu **kích thước** (`plan.md`: "< 700KB") đã đạt: 697.3KB.
- Mục tiêu **độ chính xác** đạt: INT8 chỉ rớt 0.15 điểm % so PyTorch gốc, trong ngưỡng chấp nhận 2 điểm %.
- Mục tiêu **tốc độ trên CPU dev** không chắc đạt bằng INT8 — nhưng **ONNX FP32 luôn nhanh hơn PyTorch gốc rõ rệt** (1.08ms → 0.27ms) mà không đổi gì về độ chính xác hay kích thước, nên nếu chỉ cần tối ưu tốc độ (không cần thu nhỏ file), **ONNX FP32 là lựa chọn tốt hơn INT8 trên phần cứng này**.
- Nếu mục tiêu thật sự là triển khai lên thiết bị edge có tăng tốc INT8 phần cứng (Raspberry Pi 4+ dùng ARM NEON dot-product, Jetson Nano dùng TensorRT INT8, ...), cần đo lại latency TRÊN CHÍNH thiết bị đó — số liệu latency ở đây chỉ phản ánh đúng CPU máy dev, không đại diện cho edge device thật.

## Cách tái tạo

```bash
python -m src.models.export_onnx                       # xuất resnet1d.onnx + resnet1d_int8.onnx
python -m backend.scripts.validate_onnx_classification  # đo accuracy + ghi báo cáo này
```
