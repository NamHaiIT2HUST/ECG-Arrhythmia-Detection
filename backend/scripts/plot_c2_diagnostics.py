"""
Sinh 2 bieu do minh hoa cho phan C2 (Validation split + retrain ResNet1D):

1. So sanh Validation Accuracy/Loss qua tung epoch giua 2 lan train:
   - "Truoc fix": tach Validation SAU SMOTE (lam thang ngay trong src/benchmark.py) - bi
     thoi phong gia tao (Val 99.78% nhung Test chi 98.56%).
   - "Sau fix": tach Validation TRUOC SMOTE (dung o data/preprocess.py) - Val (98.62%) khop
     sat Test (98.51%), phan anh dung nang luc that cua model.
   So lieu duoi day duoc CHEP LAI CHINH XAC tu console log that cua 2 lan chay
   `python src/benchmark.py --model ResNet1D` (khong doan/uoc luong) - de tai hien lai
   dung lich su that, khong phai chay lai code cu (code cu da duoc sua, khong con trong repo).

2. Ma tran nham lan (confusion matrix) cho ket qua danh gia end-to-end 96.62% - chay lai
   truc tiep tu backend/scripts/validate_classification.py de dam bao khop 100% voi model
   hien tai, khong chep tay.

Chay: python -m backend.scripts.plot_c2_diagnostics
Yeu cau: pip install matplotlib (da them vao requirements.txt)
"""
import os

import matplotlib
matplotlib.use("Agg")  # khong can man hinh, chi ghi file - tranh loi tren may khong co GUI
import matplotlib.pyplot as plt
import numpy as np

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")

# --- Du lieu chep tu console log that (xem docstring o tren) ---
EPOCHS = list(range(1, 11))

BEFORE_FIX = {
    "val_loss": [0.0341, 0.0222, 0.0164, 0.0140, 0.0144, 0.0133, 0.0096, 0.0091, 0.0108, 0.0077],
    "val_acc": [98.93, 99.24, 99.47, 99.60, 99.52, 99.64, 99.74, 99.74, 99.72, 99.78],
    "test_acc": 98.56,
    "label": "Trước fix (Validation tách SAU SMOTE)",
    "color": "#ef4444",
}
AFTER_FIX = {
    "val_loss": [0.0766, 0.0752, 0.0700, 0.0733, 0.0726, 0.0737, 0.0705, 0.0736, 0.0724, 0.0780],
    "val_acc": [97.58, 97.76, 98.16, 98.26, 98.50, 98.56, 98.70, 98.62, 98.62, 98.62],
    "test_acc": 98.51,
    "label": "Sau fix (Validation tách TRƯỚC SMOTE)",
    "color": "#10b981",
}


def plot_validation_leak_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for run in (BEFORE_FIX, AFTER_FIX):
        ax1.plot(EPOCHS, run["val_acc"], marker="o", color=run["color"], label=run["label"])
        ax1.axhline(run["test_acc"], color=run["color"], linestyle="--", alpha=0.5,
                     label=f"{run['label']} - Test Accuracy ({run['test_acc']}%)")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Validation Accuracy (%)")
    ax1.set_title("Validation Accuracy: trước vs sau khi sửa lỗi tách sau SMOTE")
    ax1.legend(fontsize=8, loc="lower right")
    ax1.grid(alpha=0.3)

    for run in (BEFORE_FIX, AFTER_FIX):
        ax2.plot(EPOCHS, run["val_loss"], marker="o", color=run["color"], label=run["label"])
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Validation Loss")
    ax2.set_title("Validation Loss: trước vs sau khi sửa lỗi tách sau SMOTE")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    fig.suptitle("C2 — Tách Validation sau SMOTE (giả) vs trước SMOTE (thật)", fontsize=12, fontweight="bold")
    fig.tight_layout()
    out_path = os.path.join(DOCS_DIR, "c2_validation_leak_comparison.png")
    fig.savefig(out_path, dpi=150)
    print(f"[✓] Đã lưu {out_path}")


def plot_confusion_matrix():
    # Chay lai dung pipeline that (backend/scripts/validate_classification.py) tren dung
    # 8 ban ghi da dung xuyen suot du an, dam bao khop 100% voi model dang co trong
    # saved_models/resnet1d.pth - khong chep tay so lieu.
    from backend.scripts.validate_classification import DEFAULT_RECORDS, evaluate_record
    from backend.service.inference_service import ai_service
    from sklearn.metrics import confusion_matrix

    ai_service.load_model("saved_models/resnet1d.pth")

    all_true, all_pred = [], []
    for rec in DEFAULT_RECORDS:
        y_true, y_pred = evaluate_record(rec)
        all_true.extend(y_true.tolist())
        all_pred.extend(y_pred.tolist())

    labels = [0, 1, 2, 3, 4]
    label_names = ["N", "S", "V", "F", "Q"]
    cm = confusion_matrix(all_true, all_pred, labels=labels)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels(label_names)
    ax.set_yticklabels(label_names)
    ax.set_xlabel("Dự đoán")
    ax.set_ylabel("Thật (nhãn bác sĩ)")
    ax.set_title(f"Confusion Matrix — End-to-End (8 bản ghi PhysioNet, n={cm.sum()})")

    for i in range(5):
        for j in range(5):
            color = "white" if cm_norm[i, j] > 0.5 else "black"
            ax.text(j, i, f"{cm[i, j]}\n({cm_norm[i, j]*100:.1f}%)", ha="center", va="center",
                     color=color, fontsize=8)

    fig.colorbar(im, ax=ax, label="Tỉ lệ theo hàng (thật)")
    fig.tight_layout()
    out_path = os.path.join(DOCS_DIR, "c2_confusion_matrix.png")
    fig.savefig(out_path, dpi=150)
    print(f"[✓] Đã lưu {out_path}")
    print(f"    Accuracy tổng: {np.trace(cm) / cm.sum() * 100:.2f}%")


if __name__ == "__main__":
    plot_validation_leak_comparison()
    plot_confusion_matrix()
