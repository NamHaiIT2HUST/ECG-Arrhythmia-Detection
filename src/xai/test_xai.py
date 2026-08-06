import os
import sys
import time
import torch
import numpy as np
import matplotlib.pyplot as plt

# Đảm bảo đường dẫn có thể import
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)

from models.resnet1d import ResNet1D
from xai.gradcam1d import GradCAM1D, Saliency1D

# Từ điển ánh xạ nhãn
AAMI_CLASSES = {
    0: 'Bình thường (N)',
    1: 'Trên thất (S)',
    2: 'Nhịp thất (V)',
    3: 'Hợp nhất (F)',
    4: 'Không phân loại (Q)'
}

def load_sample_data():
    """Tải 1 mẫu Bình thường (Class 0) và 1 mẫu Thất (Class 2) từ Test set"""
    x_te_path = os.path.join(PROJECT_DIR, "data", "processed", "X_test_kaggle.npy")
    y_te_path = os.path.join(PROJECT_DIR, "data", "processed", "y_test_kaggle.npy")
    
    X_test = np.load(x_te_path)
    y_test = np.load(y_te_path)
    
    # Tìm index mẫu lớp 0 và lớp 2
    idx_norm = np.where(y_test == 0)[0][0]
    idx_vent = np.where(y_test == 2)[0][10] # Lấy mẫu V thứ 10 cho rõ
    
    return [
        (torch.tensor(X_test[idx_norm], dtype=torch.float32).unsqueeze(0), y_test[idx_norm]),
        (torch.tensor(X_test[idx_vent], dtype=torch.float32).unsqueeze(0), y_test[idx_vent])
    ]

def plot_xai_comparison(model_path):
    print("=== ĐANG CHẠY BENCHMARK XAI ===")
    # 1. Khởi tạo mô hình và XAI modules
    model = ResNet1D()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    
    # Ở ResNet1D, ta lấy layer residual cuối cùng (layer4 hoặc tương tự). 
    # Nhưng trong kiến trúc đơn giản của chúng ta, lấy layer conv cuối trước pooling.
    # Ta sẽ giả sử layer cuối cùng có tên là 'conv_final' hoặc tìm layer phù hợp.
    target_layer = model.layer3
    
    gradcam = GradCAM1D(model, target_layer)
    saliency = Saliency1D(model)
    
    samples = load_sample_data()
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 8))
    fig.suptitle('So Sánh Explainable AI (XAI) cho Nhịp Tim: Grad-CAM vs Saliency Maps', fontsize=16)
    
    for row_idx, (input_tensor, true_label) in enumerate(samples):
        input_np = input_tensor.squeeze().numpy()
        x = np.arange(len(input_np))
        
        # --- Chạy Grad-CAM ---
        t0 = time.time()
        cam_heatmap, pred_cam = gradcam.generate_heatmap(input_tensor)
        t_cam = (time.time() - t0) * 1000 # ms
        
        # --- Chạy Saliency ---
        t0 = time.time()
        sal_heatmap, pred_sal = saliency.generate_heatmap(input_tensor)
        t_sal = (time.time() - t0) * 1000 # ms
        
        # --- Plot Grad-CAM ---
        ax = axes[row_idx, 0]
        ax.plot(x, input_np, label='ECG Signal', color='black', alpha=0.6)
        
        # Tô màu bằng heatmap
        for i in range(len(x)-1):
            ax.fill_between(x[i:i+2], 0, input_np[i:i+2], 
                            color=plt.cm.jet(cam_heatmap[i]), alpha=cam_heatmap[i]*0.8)
            
        label_text = AAMI_CLASSES.get(true_label, str(true_label))
        ax.set_title(f'Grad-CAM (True: {label_text} | Pred: {pred_cam})\nLatency: {t_cam:.2f} ms')
        
        # --- Plot Saliency ---
        ax = axes[row_idx, 1]
        ax.plot(x, input_np, label='ECG Signal', color='black', alpha=0.6)
        
        # Saliency thường là các chấm/nhiễu rải rác
        ax.scatter(x, input_np, c=sal_heatmap, cmap='jet', s=sal_heatmap*50, alpha=0.8)
            
        ax.set_title(f'Saliency Map (True: {label_text} | Pred: {pred_sal})\nLatency: {t_sal:.2f} ms')
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_path = os.path.join(PROJECT_DIR, "docs", "xai_comparison.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    print(f"[✓] Đã xuất ảnh so sánh ra: {output_path}")

if __name__ == "__main__":
    model_path = os.path.join(PROJECT_DIR, "saved_models", "resnet1d.pth")
    if not os.path.exists(model_path):
        print(f"[!] Không tìm thấy mô hình {model_path}. Hãy chạy train trước.")
        sys.exit(1)
        
    plot_xai_comparison(model_path)
