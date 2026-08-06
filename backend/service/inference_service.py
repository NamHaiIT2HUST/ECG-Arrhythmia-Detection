import os
import time
import torch
import numpy as np
from src.models.resnet1d import ResNet1D
from src.xai.gradcam1d import GradCAM1D

# Nhãn phân loại
AAMI_CLASSES = {
    0: 'BÌNH THƯỜNG',
    1: 'CẢNH BÁO: TRÊN THẤT (S)',
    2: 'CẢNH BÁO: NHỊP THẤT (V)',
    3: 'CẢNH BÁO: HỢP NHẤT (F)',
    4: 'CẢNH BÁO: CHƯA RÕ (Q)'
}

class ECGInferenceService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.gradcam = None
        self.is_ready = False

    def load_model(self, model_path: str):
        """Khởi tạo và nạp trọng số mô hình ResNet1D vào RAM"""
        if not os.path.exists(model_path):
            print(f"[LỖI] Không tìm thấy model tại {model_path}")
            return
            
        print(f"[+] Đang tải mô hình ResNet1D từ {model_path} lên {self.device}...")
        self.model = ResNet1D(in_channels=1, num_classes=5)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        # Khởi tạo Grad-CAM, nối vào block cuối của ResNet
        self.gradcam = GradCAM1D(self.model, self.model.layer3)
        self.is_ready = True
        print("[✓] AI Model & Grad-CAM đã sẵn sàng.")

    def predict(self, window_187):
        """
        Dự đoán trên 1 cửa sổ 187 điểm.
        - Trả về: (nhãn_chữ, heatmap_list, latency_ms)
        - Nếu là Bình thường (0), heatmap = None để tiết kiệm băng thông.
        """
        if not self.is_ready or len(window_187) != 187:
            return "CHỜ DỮ LIỆU", None, 0.0
            
        t0 = time.time()
        
        # Chuyển đổi sang Tensor
        input_np = np.array(window_187, dtype=np.float32)
        # Reshape thành (batch_size=1, channels=1, seq_len=187)
        input_tensor = torch.tensor(input_np).unsqueeze(0).unsqueeze(0).to(self.device)
        
        # Chạy model
        with torch.no_grad():
            output = self.model(input_tensor)
            pred_class = torch.argmax(output, dim=1).item()
            
        latency_ms = (time.time() - t0) * 1000
        
        heatmap_list = None
        
        # XAI (Grad-CAM) CHỈ chạy nếu phát hiện bất thường (class > 0)
        if pred_class > 0:
            t1 = time.time()
            cam, _ = self.gradcam.generate_heatmap(input_tensor.cpu())
            # Chuyển numpy array thành list chuẩn float để serialize sang JSON
            heatmap_list = [round(float(val), 4) for val in cam]
            latency_ms += (time.time() - t1) * 1000
            
        label_text = AAMI_CLASSES.get(pred_class, "KHÔNG XÁC ĐỊNH")
        
        return label_text, heatmap_list, round(latency_ms, 2)

# Khởi tạo instance toàn cục (Singleton)
ai_service = ECGInferenceService()
