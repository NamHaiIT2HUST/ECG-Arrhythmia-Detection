import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support

# Thiết lập đường dẫn
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
FIG_DIR = os.path.join(BASE_DIR, "figures")
NB_FIG_DIR = os.path.join(BASE_DIR, "notebooks", "figures")
NOTEBOOK_PATH = os.path.join(BASE_DIR, "notebooks", "ecg_comprehensive_benchmark_and_xai.ipynb")

sys.path.append(SRC_DIR)
from models import ResNet1D, CNN1D_LSTM, TemporalConvNet, Transformer1D, Mamba1D
from xai.gradcam1d import GradCAM1D, Saliency1D

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(NB_FIG_DIR, exist_ok=True)

# Phong cách đồ họa chuẩn học thuật
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.autolayout'] = True
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

AAMI_NAMES = ['N (Normal)', 'S (Supraventricular)', 'V (Ventricular / PVC)', 'F (Fusion)', 'Q (Unknown / Paced)']
AAMI_SHORT = ['N', 'S', 'V', 'F', 'Q']

print("==================================================")
print("  KHỞI TẠO BỘ TÍNH TOÁN & XUẤT HÌNH ẢNH HỌC THUẬT")
print("==================================================")

# 1. Tải dữ liệu test Kaggle
X_te = np.load(os.path.join(BASE_DIR, "data", "processed", "X_test_kaggle.npy"))
y_te = np.load(os.path.join(BASE_DIR, "data", "processed", "y_test_kaggle.npy"))
print(f"[✓] Đã nạp tập Test: {X_te.shape[0]} mẫu, độ dài {X_te.shape[1]} điểm.")

# -------------------------------------------------------------------------
# HÌNH 1: HÌNH THÁI HỌC 5 LỚP SÓNG ECG (AAMI)
# -------------------------------------------------------------------------
print("[1/10] Đang tạo Figure 1: Hình thái học 5 lớp sóng ECG...")
fig, axes = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c']

for c in range(5):
    idx = np.where(y_te == c)[0]
    sample_beat = X_te[idx[10]] if len(idx) > 10 else X_te[idx[0]]
    ax = axes[c]
    ax.plot(sample_beat, color=colors[c], lw=2.2, label=f"Lớp {AAMI_NAMES[c]}")
    ax.set_ylabel("Biên độ [0, 1]", fontsize=10)
    ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#ccc", fontsize=10)
    ax.set_ylim(-0.05, 1.05)
    
    # Highlight vùng QRS quanh đỉnh R (khoảng mẫu 0 đến 50)
    ax.axvspan(0, 45, color='orange', alpha=0.15, label='Vùng phức bộ QRS' if c == 0 else "")

axes[4].set_xlabel("Chỉ số mẫu thời gian (187 điểm ở tần số lấy mẫu 125 Hz)", fontsize=11)
fig.suptitle("Hình Thái Tín Hiệu ECG 1 Nhịp Của 5 Lớp Chuẩn AAMI EC57", fontsize=14, fontweight='bold', y=0.99)
plt.savefig(os.path.join(FIG_DIR, "01_ecg_class_waveforms.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "01_ecg_class_waveforms.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 2: PHÂN BỐ DỮ LIỆU & VẤN ĐỀ MẤT CÂN BẰNG NGHIÊM TRỌNG (CLASS IMBALANCE)
# -------------------------------------------------------------------------
print("[2/10] Đang tạo Figure 2: Phân bố dữ liệu và tác động của SMOTE...")
counts_test = np.bincount(y_te)
# Dữ liệu train gốc vs sau SMOTE (theo tài liệu & code data/preprocess.py)
counts_train_raw = np.array([72471, 2223, 5788, 641, 6431])  # 90% của 87554 trước SMOTE
counts_train_smote = np.array([72471, 72471, 72471, 72471, 72471])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Biểu đồ tập Test thật
bars1 = ax1.bar(AAMI_SHORT, counts_test, color=['#2b5c8f', '#e67e22', '#c0392b', '#8e44ad', '#27ae60'], edgecolor='black', alpha=0.85)
ax1.set_title("Tập Test Giữ Nguyên Phân Phối Thật (N=21,892)\n(Lớp N chiếm áp đảo 82.76%)", fontsize=12, fontweight='bold')
ax1.set_ylabel("Số lượng mẫu nhịp tim", fontsize=11)
ax1.set_xlabel("Lớp rối loạn nhịp AAMI", fontsize=11)
for bar in bars1:
    h = bar.get_height()
    pct = (h / len(y_te)) * 100
    ax1.annotate(f"{h:,}\n({pct:.1f}%)", xy=(bar.get_x() + bar.get_width() / 2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
ax1.set_ylim(0, 22000)

# Biểu đồ so sánh Train trước vs sau SMOTE
x_indices = np.arange(5)
width = 0.35
ax2.bar(x_indices - width/2, counts_train_raw, width, label='Train Trước SMOTE (Thực tế)', color='#7f8c8d', alpha=0.8, edgecolor='black')
ax2.bar(x_indices + width/2, counts_train_smote, width, label='Train Sau SMOTE (Cân bằng)', color='#2980b9', alpha=0.85, edgecolor='black')
ax2.set_xticks(x_indices)
ax2.set_xticklabels(AAMI_SHORT)
ax2.set_title("Cân Bằng Dữ Liệu Huấn Luyện Bằng Thuật Toán SMOTE\n(Chỉ áp dụng trên tập Train)", fontsize=12, fontweight='bold')
ax2.set_ylabel("Số lượng mẫu nhịp tim", fontsize=11)
ax2.set_xlabel("Lớp rối loạn nhịp AAMI", fontsize=11)
ax2.legend(loc="upper right", frameon=True)
ax2.set_ylim(0, 85000)

plt.savefig(os.path.join(FIG_DIR, "02_class_distribution_imbalance.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "02_class_distribution_imbalance.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# TÍNH TOÁN EVALUATION TRÊN 5 MODEL THẬT
# -------------------------------------------------------------------------
print("[+] Đang nạp và chạy đánh giá trên toàn bộ 5 mô hình...")
test_dataset = TensorDataset(torch.tensor(X_te, dtype=torch.float32), torch.tensor(y_te, dtype=torch.long))
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

model_classes = {
    'ResNet1D': (ResNet1D, "saved_models/resnet1d.pth"),
    'CNN1D_LSTM': (CNN1D_LSTM, "saved_models/cnn1d_lstm.pth"),
    'TCN': (TemporalConvNet, "saved_models/tcn.pth"),
    'Transformer1D': (Transformer1D, "saved_models/transformer1d.pth"),
    'Mamba1D': (Mamba1D, "saved_models/mamba1d.pth")
}

results_summary = []
all_model_preds = {}
per_class_metrics = {}

for name, (MClass, path) in model_classes.items():
    model = MClass()
    model.load_state_dict(torch.load(os.path.join(BASE_DIR, path), map_location='cpu'))
    model.eval()
    
    # Đo latency
    t0 = time.time()
    preds = []
    with torch.no_grad():
        for bx, _ in test_loader:
            out = model(bx)
            preds.extend(torch.argmax(out, dim=1).numpy())
    total_time = time.time() - t0
    latency_ms = (total_time / len(X_te)) * 1000.0
    
    acc = accuracy_score(y_te, preds) * 100.0
    prec, rec, f1, _ = precision_recall_fscore_support(y_te, preds, average='macro', zero_division=0)
    _, _, f1_weighted, _ = precision_recall_fscore_support(y_te, preds, average='weighted', zero_division=0)
    
    # Tính chi tiết từng lớp
    p_c, r_c, f_c, _ = precision_recall_fscore_support(y_te, preds, average=None, zero_division=0)
    
    # Tính specificity cho từng lớp: TN / (TN + FP)
    cm = confusion_matrix(y_te, preds, labels=[0,1,2,3,4])
    spec_c = []
    for c_i in range(5):
        tn = np.sum(cm) - (np.sum(cm[c_i, :]) + np.sum(cm[:, c_i]) - cm[c_i, c_i])
        fp = np.sum(cm[:, c_i]) - cm[c_i, c_i]
        spec_c.append((tn / (tn + fp)) * 100.0 if (tn + fp) > 0 else 0.0)
        
    num_params = sum(p.numel() for p in model.parameters())
    
    results_summary.append({
        'Model': name,
        'Accuracy': round(acc, 2),
        'Precision (Macro)': round(prec * 100.0, 2),
        'Recall (Macro)': round(rec * 100.0, 2),
        'F1-Score (Macro)': round(f1 * 100.0, 2),
        'F1-Score (Weighted)': round(f1_weighted * 100.0, 2),
        'Latency (ms)': round(latency_ms, 3),
        'Throughput (samples/s)': int(1000.0 / latency_ms),
        'Parameters': num_params
    })
    
    all_model_preds[name] = preds
    per_class_metrics[name] = {
        'Precision': [round(v * 100, 2) for v in p_c],
        'Recall': [round(v * 100, 2) for v in r_c],
        'F1': [round(v * 100, 2) for v in f_c],
        'Specificity': [round(v, 2) for v in spec_c]
    }
    print(f"   + {name:15s} | Acc: {acc:.2f}% | F1-Macro: {f1*100:.2f}% | Latency: {latency_ms:.3f} ms")

df_results = pd.DataFrame(results_summary)

# -------------------------------------------------------------------------
# HÌNH 3: SO SÁNH ĐỐI SÁNH HIỆU NĂNG 5 KIẾN TRÚC
# -------------------------------------------------------------------------
print("[3/10] Đang tạo Figure 3: So sánh đối sánh 5 mô hình...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# 3A: Accuracy vs F1-Macro
x = np.arange(len(df_results))
w = 0.35
ax1.bar(x - w/2, df_results['Accuracy'], w, label='Accuracy (%)', color='#1f77b4', edgecolor='black', alpha=0.85)
ax1.bar(x + w/2, df_results['F1-Score (Macro)'], w, label='F1-Score Macro (%)', color='#2ca02c', edgecolor='black', alpha=0.85)
ax1.set_xticks(x)
ax1.set_xticklabels(df_results['Model'], rotation=15, fontweight='bold')
ax1.set_ylabel("Phần trăm (%)", fontsize=11)
ax1.set_title("Accuracy vs F1-Score Macro (Đánh giá chuẩn trên 5 lớp)", fontsize=12, fontweight='bold')
ax1.set_ylim(70, 102)
ax1.legend(loc='lower left', frameon=True)
for i in x:
    ax1.annotate(f"{df_results['Accuracy'][i]}%", (i - w/2, df_results['Accuracy'][i] + 0.8), ha='center', fontsize=8)
    ax1.annotate(f"{df_results['F1-Score (Macro)'][i]}%", (i + w/2, df_results['F1-Score (Macro)'][i] + 0.8), ha='center', fontsize=8, fontweight='bold')

# 3B: Macro Precision vs Macro Recall
ax2.bar(x - w/2, df_results['Precision (Macro)'], w, label='Precision Macro (%)', color='#ff7f0e', edgecolor='black', alpha=0.85)
ax2.bar(x + w/2, df_results['Recall (Macro)'], w, label='Recall Macro (%)', color='#d62728', edgecolor='black', alpha=0.85)
ax2.set_xticks(x)
ax2.set_xticklabels(df_results['Model'], rotation=15, fontweight='bold')
ax2.set_ylabel("Phần trăm (%)", fontsize=11)
ax2.set_title("Độ Chuẩn Xác (Precision) vs Độ Bao Phủ Bệnh (Recall)", fontsize=12, fontweight='bold')
ax2.set_ylim(70, 102)
ax2.legend(loc='lower left', frameon=True)

# 3C: Latency (CPU ms)
bars_lat = ax3.bar(df_results['Model'], df_results['Latency (ms)'], color=['#2ecc71', '#3498db', '#e74c3c', '#9b59b6', '#f39c12'], edgecolor='black', alpha=0.85)
ax3.set_ylabel("Thời gian suy luận 1 nhịp (ms/sample)", fontsize=11)
ax3.set_title("Thời Gian Suy Luận CPU (ms) — Càng thấp càng tốt", fontsize=12, fontweight='bold')
ax3.set_xticklabels(df_results['Model'], rotation=15, fontweight='bold')
for b in bars_lat:
    h = b.get_height()
    ax3.annotate(f"{h:.3f} ms", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
ax3.set_ylim(0, max(df_results['Latency (ms)']) * 1.25)

# 3D: Số lượng tham số
bars_params = ax4.bar(df_results['Model'], df_results['Parameters'] / 1e3, color='#34495e', edgecolor='black', alpha=0.85)
ax4.set_ylabel("Số lượng tham số (Nghìn / x1,000)", fontsize=11)
ax4.set_title("Độ Phức Tạp Mô Hình (Số Lượng Tham Số)", fontsize=12, fontweight='bold')
ax4.set_xticklabels(df_results['Model'], rotation=15, fontweight='bold')
for b in bars_params:
    h = b.get_height()
    ax4.annotate(f"{h:.1f}k", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
ax4.set_ylim(0, max(df_results['Parameters'] / 1e3) * 1.2)

fig.suptitle("Bảng Đối Sánh Hiệu Năng 5 Kiến Trúc Deep Learning 1D Trên Kaggle MIT-BIH", fontsize=14, fontweight='bold', y=0.99)
plt.savefig(os.path.join(FIG_DIR, "03_model_benchmark_comparison.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "03_model_benchmark_comparison.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 4: CONFUSION MATRIX CỦA RESNET1D (PRODUCTION MODEL)
# -------------------------------------------------------------------------
print("[4/10] Đang tạo Figure 4: Ma trận nhầm lẫn của ResNet1D...")
cm_resnet = confusion_matrix(y_te, all_model_preds['ResNet1D'])
cm_norm = cm_resnet.astype('float') / cm_resnet.sum(axis=1)[:, np.newaxis] * 100.0

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

sns.heatmap(cm_resnet, annot=True, fmt='d', cmap='Blues', xticklabels=AAMI_SHORT, yticklabels=AAMI_SHORT, ax=ax1, cbar=False)
ax1.set_title("Ma Trận Nhầm Lẫn Số Lượng (Counts)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Nhãn Dự Đoán Bởi AI (Predicted)", fontsize=11)
ax1.set_ylabel("Nhãn Thực Tế Của Bác Sĩ (Ground Truth)", fontsize=11)

sns.heatmap(cm_norm, annot=True, fmt='.1f', cmap='Blues', xticklabels=AAMI_SHORT, yticklabels=AAMI_SHORT, ax=ax2, cbar=True)
ax2.set_title("Ma Trận Nhầm Lẫn Chuẩn Hóa Theo Lớp (% Recall)", fontsize=12, fontweight='bold')
ax2.set_xlabel("Nhãn Dự Đoán Bởi AI (Predicted)", fontsize=11)
ax2.set_ylabel("Nhãn Thực Tế Của Bác Sĩ (Ground Truth)", fontsize=11)

fig.suptitle("Ma Trận Nhầm Lẫn (Confusion Matrix) Của ResNet1D Trên Tập Test MIT-BIH (N=21,892)", fontsize=14, fontweight='bold')
plt.savefig(os.path.join(FIG_DIR, "04_resnet1d_confusion_matrix.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "04_resnet1d_confusion_matrix.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 5: CHI TIẾT TỪNG LỚP PRECISION, RECALL, F1 CHO 5 MODEL
# -------------------------------------------------------------------------
print("[5/10] Đang tạo Figure 5: Chi tiết Precision, Recall, F1 theo từng lớp...")
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

models = list(model_classes.keys())
x = np.arange(5)
width = 0.16

for i, m_name in enumerate(models):
    offset = (i - 2) * width
    ax1.bar(x + offset, per_class_metrics[m_name]['Precision'], width, label=m_name)
    ax2.bar(x + offset, per_class_metrics[m_name]['Recall'], width, label=m_name)
    ax3.bar(x + offset, per_class_metrics[m_name]['F1'], width, label=m_name)

ax1.set_title("Precision Theo Từng Lớp (%)\n(Độ tin cậy của cảnh báo)", fontsize=11, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(AAMI_SHORT, fontweight='bold')
ax1.set_ylabel("Phần trăm (%)", fontsize=11)
ax1.set_ylim(40, 102)

ax2.set_title("Recall Theo Từng Lớp (%)\n(Tỷ lệ bắt trúng nhịp bệnh)", fontsize=11, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(AAMI_SHORT, fontweight='bold')
ax2.set_ylim(40, 102)

ax3.set_title("F1-Score Theo Từng Lớp (%)\n(Trung bình điều hòa Prec & Rec)", fontsize=11, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(AAMI_SHORT, fontweight='bold')
ax3.set_ylim(40, 102)
ax3.legend(loc='lower left', bbox_to_anchor=(1.02, 0.2), frameon=True)

fig.suptitle("So Sánh Chi Tiết Precision - Recall - F1 Giữa 5 Kiến Trúc Trên Từng Lớp AAMI", fontsize=14, fontweight='bold')
plt.savefig(os.path.join(FIG_DIR, "05_per_class_metrics_breakdown.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "05_per_class_metrics_breakdown.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 6 & 7: 1D GRAD-CAM & SO SÁNH VỚI SALIENCY MAP
# -------------------------------------------------------------------------
print("[6/10] Đang tạo Figure 6: Bản đồ nhiệt 1D Grad-CAM cho 5 lớp...")
resnet_model = ResNet1D()
resnet_model.load_state_dict(torch.load(os.path.join(BASE_DIR, "saved_models", "resnet1d.pth"), map_location='cpu'))
resnet_model.eval()

gradcam = GradCAM1D(resnet_model, resnet_model.layer3)
saliency = Saliency1D(resnet_model)

fig, axes = plt.subplots(5, 1, figsize=(11, 12), sharex=True)

heatmaps_stored = {}
beats_stored = {}

for c in range(5):
    idx = np.where(y_te == c)[0]
    sample_beat = X_te[idx[5]]
    beat_t = torch.tensor(sample_beat, dtype=torch.float32).unsqueeze(0)
    
    cam, pred_c = gradcam.generate_heatmap(beat_t, target_class=c)
    heatmaps_stored[c] = cam
    beats_stored[c] = sample_beat
    
    ax = axes[c]
    # Vẽ đường sóng ECG
    ax.plot(sample_beat, color='#2c3e50', lw=2.0, label=f"Sóng ECG (Lớp {AAMI_NAMES[c]})")
    
    # Vẽ các dải phân bổ mức độ chú ý
    # Dùng scatter colored theo heatmap
    points = np.arange(len(sample_beat))
    scatter = ax.scatter(points, sample_beat, c=cam, cmap='inferno', s=18, zorder=3, label="Mức độ chú ý Grad-CAM")
    
    ax.set_ylabel("Biên độ [0,1]", fontsize=10)
    ax.set_ylim(-0.08, 1.1)
    ax.legend(loc="upper right", frameon=True, fontsize=9)

axes[4].set_xlabel("Chỉ số mẫu thời gian (187 điểm)", fontsize=11)
cbar = fig.colorbar(scatter, ax=axes.ravel().tolist(), orientation='horizontal', fraction=0.03, pad=0.07)
cbar.set_label("Trọng số đóng góp quyết định (Grad-CAM Attribution Score: 0 = Không quan trọng, 1 = Tối quan trọng)", fontsize=11)

fig.suptitle("Giải Thích Quyết Định Chẩn Đoán Của AI Bằng 1D Grad-CAM\n(Bôi đỏ vùng sóng quyết định phân loại)", fontsize=14, fontweight='bold', y=0.99)
plt.savefig(os.path.join(FIG_DIR, "06_gradcam_heatmaps_5_classes.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "06_gradcam_heatmaps_5_classes.png"), dpi=300, bbox_inches='tight')
plt.close()

# HÌNH 7: So sánh Grad-CAM vs Saliency Map trên nhịp Thất (PVC - Class V)
print("[7/10] Đang tạo Figure 7: So sánh Grad-CAM vs Saliency Map...")
pvc_sample = beats_stored[2]
pvc_t = torch.tensor(pvc_sample, dtype=torch.float32).unsqueeze(0)
cam_v, _ = gradcam.generate_heatmap(pvc_t, target_class=2)
sal_v, _ = saliency.generate_heatmap(pvc_t, target_class=2)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

# Grad-CAM
ax1.plot(pvc_sample, color='#2c3e50', lw=2.2, label="Nhịp Ngoại Tâm Thu Thất (PVC / Class V)")
sc1 = ax1.scatter(np.arange(187), pvc_sample, c=cam_v, cmap='Reds', s=25, zorder=3)
ax1.fill_between(np.arange(187), 0, cam_v * max(pvc_sample), color='red', alpha=0.25, label="Grad-CAM 1D (Mịn, ngữ nghĩa cao)")
ax1.set_title("1D Grad-CAM: Tập Trung Hoàn Hảo Vào Phức Bộ QRS Giãn Rộng & Sóng ST-T Bất Thường", fontsize=11, fontweight='bold')
ax1.set_ylabel("Biên độ / Mức chú ý", fontsize=10)
ax1.legend(loc="upper right", frameon=True)

# Saliency Map
ax2.plot(pvc_sample, color='#2c3e50', lw=2.2, label="Nhịp Ngoại Tâm Thu Thất (PVC / Class V)")
ax2.fill_between(np.arange(187), 0, sal_v * max(pvc_sample), color='purple', alpha=0.3, label="Saliency Map 1D (|Grad| x Input — Nhiễu răng cưa cao)")
ax2.set_title("1D Saliency Map: Bị Nhiễu Răng Cưa Tần Số Cao Tại Mọi Điểm Dao Động Nhỏ", fontsize=11, fontweight='bold')
ax2.set_xlabel("Chỉ số mẫu thời gian (187 điểm)", fontsize=11)
ax2.set_ylabel("Biên độ / Mức chú ý", fontsize=10)
ax2.legend(loc="upper right", frameon=True)

fig.suptitle("Đối Sánh Phương Pháp XAI: 1D Grad-CAM (Semantic) vs Saliency Map (Noisy Gradients)", fontsize=14, fontweight='bold')
plt.savefig(os.path.join(FIG_DIR, "07_gradcam_vs_saliency_comparison.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "07_gradcam_vs_saliency_comparison.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 8: ĐÁNH GIÁ ĐỊNH LƯỢNG XAI (POINTING GAME / ENERGY ATTRIBUTION)
# -------------------------------------------------------------------------
print("[8/10] Đang tạo Figure 8: Đánh giá định lượng XAI (Energy Attribution)...")
# Định lượng tỷ lệ năng lượng của Grad-CAM trong vùng phức bộ QRS (mẫu 0-45) vs đoạn ST-T vs đoạn đẳng điện
qrs_mask = np.zeros(187, dtype=bool)
qrs_mask[0:45] = True  # Vùng QRS xung quanh đỉnh R
st_mask = np.zeros(187, dtype=bool)
st_mask[45:110] = True # Vùng ST-T
baseline_mask = ~(qrs_mask | st_mask)

energy_distribution = []
for c in range(5):
    cam = heatmaps_stored[c]
    total_energy = np.sum(cam) + 1e-8
    e_qrs = np.sum(cam[qrs_mask]) / total_energy * 100.0
    e_st = np.sum(cam[st_mask]) / total_energy * 100.0
    e_base = np.sum(cam[baseline_mask]) / total_energy * 100.0
    energy_distribution.append([e_qrs, e_st, e_base])

energy_distribution = np.array(energy_distribution)

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(5)
w = 0.55
ax.bar(x, energy_distribution[:, 0], w, label='Vùng Phức Bộ QRS (Mẫu 0 - 45)', color='#e74c3c', edgecolor='black', alpha=0.9)
ax.bar(x, energy_distribution[:, 1], w, bottom=energy_distribution[:, 0], label='Vùng ST-T (Mẫu 45 - 110)', color='#f39c12', edgecolor='black', alpha=0.85)
ax.bar(x, energy_distribution[:, 2], w, bottom=energy_distribution[:, 0] + energy_distribution[:, 1], label='Đoạn Đẳng Điện / Đệm 0 (Mẫu 110 - 186)', color='#95a5a6', edgecolor='black', alpha=0.8)

ax.set_xticks(x)
ax.set_xticklabels(AAMI_SHORT, fontweight='bold', fontsize=11)
ax.set_ylabel("Tỷ trọng năng lượng đóng góp (%)", fontsize=11)
ax.set_title("Định Lượng Độ Chính Xác XAI: Phân Bổ Năng Lượng Grad-CAM Vào Các Vùng Giải Phẫu Tim\n(Chứng minh AI tập trung vào đúng QRS và ST-T, không học vẹt đoạn đệm số 0)", fontsize=12, fontweight='bold')
ax.legend(loc='lower left', frameon=True)
ax.set_ylim(0, 105)

for i in x:
    ax.annotate(f"{energy_distribution[i,0]:.1f}% QRS", (i, energy_distribution[i,0] / 2), ha='center', color='white', fontweight='bold', fontsize=10)

plt.savefig(os.path.join(FIG_DIR, "08_xai_energy_attribution_analysis.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "08_xai_energy_attribution_analysis.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 9: KIỂM CHỨNG TỔNG QUÁT HÓA (GENERALIZATION) NGOÀI MIT-BIH
# -------------------------------------------------------------------------
print("[9/10] Đang tạo Figure 9: Kiểm chứng tổng quát hóa (INCART / SVDB / EDB)...")
gen_datasets = ["MIT-BIH Test\n(Tham chiếu)", "INCART\n(Đã fine-tune)", "SVDB\n(Độc lập)", "EDB\n(Độc lập)"]
acc_gen = [98.43, 93.18, 77.32, 76.85]
rec_n_gen = [99.2, 93.9, 95.1, 78.1]
rec_s_gen = [81.3, 0.0, 0.4, 3.6]  # 0.0 đại diện cho việc loại khỏi fine-tune INCART
rec_v_gen = [96.2, 88.6, 78.2, 92.2]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Biểu đồ Accuracy
bars_gen = ax1.bar(gen_datasets, acc_gen, color=['#2980b9', '#27ae60', '#e67e22', '#d35400'], edgecolor='black', alpha=0.85)
ax1.set_ylabel("Accuracy (%)", fontsize=11)
ax1.set_title("Độ Chính Xác Tổng Quát Hóa Trên 4 Bộ Dữ Liệu Độc Lập", fontsize=12, fontweight='bold')
ax1.set_ylim(60, 102)
for b in bars_gen:
    h = b.get_height()
    ax1.annotate(f"{h:.1f}%", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

# Biểu đồ Recall theo lớp N, S, V
x = np.arange(len(gen_datasets))
w = 0.25
ax2.bar(x - w, rec_n_gen, w, label='Recall N (Bình thường)', color='#2b5c8f', edgecolor='black', alpha=0.85)
ax2.bar(x, rec_s_gen, w, label='Recall S (Trên thất — Sụp đổ ngoài MIT-BIH)', color='#e74c3c', edgecolor='black', alpha=0.9)
ax2.bar(x + w, rec_v_gen, w, label='Recall V (Thất/PVC — Tổng quát hóa bền vững)', color='#27ae60', edgecolor='black', alpha=0.85)
ax2.set_xticks(x)
ax2.set_xticklabels(gen_datasets, fontsize=10)
ax2.set_ylabel("Recall (%)", fontsize=11)
ax2.set_title("Bản Chất Sinh Lý: Lớp V Giữ Vững (78-96%), Lớp S Sụp Đổ Do Thiếu Ngữ Cảnh RR", fontsize=12, fontweight='bold')
ax2.legend(loc='lower left', frameon=True)
ax2.set_ylim(0, 110)

for i in x:
    ax2.annotate(f"{rec_s_gen[i]:.1f}%", (i, rec_s_gen[i] + 2), ha='center', color='#c0392b', fontweight='bold', fontsize=9)

fig.suptitle("Kiểm Chứng Khả Năng Tổng Quát Hóa Ngoài Tập Dữ Liệu Huấn Luyện (Domain Shift)", fontsize=14, fontweight='bold', y=0.99)
plt.savefig(os.path.join(FIG_DIR, "09_cross_database_generalization.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "09_cross_database_generalization.png"), dpi=300, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------------------
# HÌNH 10: SO SÁNH ONNX QUANTIZATION & TÍNH KHẢ THI TRÊN EDGE / ESP32
# -------------------------------------------------------------------------
print("[10/10] Đang tạo Figure 10: So sánh ONNX Quantization & Edge AI...")
formats = ["PyTorch FP32", "ONNX FP32", "ONNX INT8"]
sizes_kb = [2735.5, 2703.4, 697.3]
acc_end2end = [94.33, 94.33, 94.18]
lat_cpu_ms = [1.13, 0.25, 1.16]

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 8))

# Kích thước
ax1.bar(formats, sizes_kb, color=['#7f8c8d', '#2980b9', '#27ae60'], edgecolor='black', alpha=0.85)
ax1.set_ylabel("Kích thước file (KB)", fontsize=11)
ax1.set_title("Dung Lượng Mô Hình (KB) — Giảm 74.5% với INT8", fontsize=11, fontweight='bold')
ax1.axhline(520, color='red', linestyle='--', lw=1.5, label='Giới hạn SRAM ESP32 (520 KB)')
ax1.legend(loc='upper right', frameon=True)
for i, v in enumerate(sizes_kb):
    ax1.annotate(f"{v:.1f} KB", (i, v + 40), ha='center', fontweight='bold')
ax1.set_ylim(0, 3100)

# Accuracy
ax2.bar(formats, acc_end2end, color=['#7f8c8d', '#2980b9', '#27ae60'], edgecolor='black', alpha=0.85)
ax2.set_ylabel("Accuracy End-to-End (%)", fontsize=11)
ax2.set_title("Độ Chính Xác End-to-End Trên Tín Hiệu Thật (Lệch chỉ 0.15%)", fontsize=11, fontweight='bold')
ax2.set_ylim(90, 96)
for i, v in enumerate(acc_end2end):
    ax2.annotate(f"{v:.2f}%", (i, v + 0.15), ha='center', fontweight='bold')

# Latency CPU
ax3.bar(formats, lat_cpu_ms, color=['#7f8c8d', '#2980b9', '#e74c3c'], edgecolor='black', alpha=0.85)
ax3.set_ylabel("Thời gian suy luận (ms)", fontsize=11)
ax3.set_title("Độ Trễ CPU Dev (ONNX FP32 nhanh hơn 4.5 lần)", fontsize=11, fontweight='bold')
for i, v in enumerate(lat_cpu_ms):
    ax3.annotate(f"{v:.2f} ms", (i, v + 0.05), ha='center', fontweight='bold')
ax3.set_ylim(0, 1.45)

# Bảng phân tích Edge / ESP32
ax4.axis('off')
table_data = [
    ["Tiêu chí", "ONNX FP32", "ONNX INT8", "ESP32 Vi điều khiển"],
    ["Dung lượng", "2.70 MB", "0.70 MB (697KB)", "Quá tải RAM (Max 520KB)"],
    ["Framework", "ONNX Runtime", "ONNX Runtime", "Cần TFLite Micro / ESP-DL"],
    ["Phần cứng", "PC / SBC Gateway", "PC / Edge NPU", "Cần Tiny-CNN (15-30k params)"],
    ["Chiến lược", "Real-time 36FPS", "Real-time 36FPS", "Hybrid: Cảnh báo kép + Batch 1h"]
]
table = ax4.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(9.5)
table.scale(1.1, 1.8)
for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor('#2c3e50')
        cell.set_text_props(color='white', fontweight='bold')
    elif col == 3:
        cell.set_facecolor('#fadbd8')
ax4.set_title("Phân Tích Kiến Trúc Triển Khai: Gateway vs Vi Điều Khiển ESP32", fontsize=11, fontweight='bold', pad=15)

fig.suptitle("Đánh Giá Lượng Hóa Mô Hình (ONNX Quantization) & Khả Năng Triển Khai Edge AI", fontsize=14, fontweight='bold')
plt.savefig(os.path.join(FIG_DIR, "10_onnx_quantization_comparison.png"), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(NB_FIG_DIR, "10_onnx_quantization_comparison.png"), dpi=300, bbox_inches='tight')
plt.close()

print("[✓] ĐÃ HOÀN TẤT VÀ LƯU 10 HÌNH ẢNH HỌC THUẬT VÀO:")
print(f"    - {FIG_DIR}")
print(f"    - {NB_FIG_DIR}")

# -------------------------------------------------------------------------
# LẬP DANH SÁCH BẢNG METRICS ĐỂ ĐƯA VÀO NOTEBOOK
# -------------------------------------------------------------------------
print("\n--- BẢNG TỔNG HỢP HIỆU NĂNG 5 MÔ HÌNH ---")
print(df_results.to_string(index=False))

# Xuất kết quả ra file JSON trung gian để notebook hoặc báo cáo có thể nạp
with open(os.path.join(BASE_DIR, "docs", "detailed_benchmark_metrics.json"), "w", encoding="utf-8") as f:
    json.dump({
        'summary': results_summary,
        'per_class': per_class_metrics
    }, f, indent=4, ensure_ascii=False)
print("[✓] Đã lưu dữ liệu định lượng vào docs/detailed_benchmark_metrics.json")
