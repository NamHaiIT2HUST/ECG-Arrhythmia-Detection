"""
Sinh 2 biểu đồ tổng quan bổ sung cho docs/ai_results_gallery.md:

1. So sánh 5 kiến trúc model trên benchmark nội bộ MIT-BIH (Accuracy/F1/Latency).
2. So sánh khả năng generalization (Accuracy + Recall N/V) qua 4 bộ dữ liệu độc lập
   (MIT-BIH Test, INCART sau fine-tune, SVDB, EDB).

Số liệu CHÉP LẠI CHÍNH XÁC từ docs/benchmark_results.md và docs/onnx_comparison.md (không
đoán/ước lượng) - để tái hiện đúng lịch sử thật, không phải chạy lại toàn bộ pipeline (tốn
nhiều phút train + cần tải INCART/SVDB/EDB).

Chạy: python -m backend.scripts.plot_ai_overview
"""
import os

import matplotlib

matplotlib.use("Agg")  # không cần màn hình, chỉ ghi file
import matplotlib.pyplot as plt
import numpy as np

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")


def plot_benchmark_5_models():
    models = ["ResNet1D", "CNN1D_LSTM", "TCN", "Transformer1D", "Mamba1D"]
    accuracy = [98.57, 97.27, 96.17, 95.36, 94.45]
    f1_macro = [92.16, 85.79, 82.81, 83.11, 79.28]
    latency_ms = [0.1342, 0.18, 0.793, 0.4294, 0.4696]
    colors = ["#10b981", "#3b82f6", "#3b82f6", "#3b82f6", "#3b82f6"]  # ResNet1D nổi bật

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    x = np.arange(len(models))
    width = 0.35
    ax1.bar(x - width / 2, accuracy, width, label="Accuracy (%)", color=colors, alpha=0.9)
    ax1.bar(x + width / 2, f1_macro, width, label="F1-macro (%)", color=colors, alpha=0.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=15)
    ax1.set_ylabel("%")
    ax1.set_ylim(70, 100)
    ax1.set_title("Accuracy & F1-macro — Benchmark nội bộ MIT-BIH")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    bars = ax2.bar(models, latency_ms, color=colors)
    ax2.set_ylabel("Latency suy luận / nhịp (ms)")
    ax2.set_title("Latency suy luận (thấp hơn = tốt hơn)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=15)
    ax2.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, latency_ms):
        ax2.text(bar.get_x() + bar.get_width() / 2, val, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    fig.suptitle("So sánh 5 kiến trúc 1D — ResNet1D được chọn triển khai (cao nhất Accuracy/F1, thấp nhất Latency)",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    out_path = os.path.join(DOCS_DIR, "ai_benchmark_5_models.png")
    fig.savefig(out_path, dpi=150)
    print(f"[OK] Da luu {out_path}")


def plot_generalization_across_datasets():
    datasets = ["MIT-BIH Test\n(tham chiếu)", "INCART\n(đã fine-tune)", "SVDB", "EDB"]
    accuracy = [98.43, 93.18, 77.32, 76.85]
    recall_n = [99.2, 93.9, 95.1, 78.1]
    recall_v = [96.2, 88.6, 78.2, 92.2]
    recall_s = [81.3, np.nan, 0.4, 3.6]  # S sụp đổ trên SVDB/EDB, không đo trên INCART held-out

    x = np.arange(len(datasets))
    width = 0.2

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - width, accuracy, width, label="Accuracy tổng", color="#6366f1")
    ax.bar(x, recall_n, width, label="Recall N", color="#10b981")
    ax.bar(x + width, recall_v, width, label="Recall V (PVC)", color="#f59e0b")
    ax.bar(x + 2 * width, np.nan_to_num(recall_s, nan=0), width, label="Recall S", color="#ef4444")

    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylabel("%")
    ax.set_ylim(0, 105)
    ax.set_title("Generalization ngoài MIT-BIH: N & V ổn định, S sụp đổ trên dữ liệu hoàn toàn mới")
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(0, color="black", linewidth=0.8)

    fig.tight_layout()
    out_path = os.path.join(DOCS_DIR, "ai_generalization_datasets.png")
    fig.savefig(out_path, dpi=150)
    print(f"[OK] Da luu {out_path}")


if __name__ == "__main__":
    plot_benchmark_5_models()
    plot_generalization_across_datasets()
