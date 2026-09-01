import os
import time
import torch
from src.models.resnet1d import ResNet1D
from src.xai.gradcam1d import GradCAM1D
from backend.core.signal_processing import normalize_window

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
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        
        # Khởi tạo Grad-CAM, nối vào block cuối của ResNet
        self.gradcam = GradCAM1D(self.model, self.model.layer3)
        self.is_ready = True
        print(f"[✓] AI Model & Grad-CAM đã sẵn sàng trên {self.device}.")

    def predict(self, beat_window):
        """
        Dự đoán trên 1 nhịp tim đã được cắt theo đỉnh R (xem `backend/core/qrs_detector.py`),
        độ dài đúng 187 điểm.
        - Trả về: (nhãn_chữ, heatmap_list, latency_ms, confidence)
        - Nếu là Bình thường (0), heatmap = None để tiết kiệm băng thông.
        - `confidence`: xác suất softmax của lớp được chọn (0-1) — dùng cho CP4.5 (ngưỡng nhạy AI)
          và CP5.3 (lưu kèm mỗi sự kiện bất thường vào DB).

        BUG FIX: Grad-CAM cần gradient nên KHÔNG dùng torch.no_grad().
        Thay vào đó, tách 2 bước: predict nhanh với no_grad, chỉ bật grad khi cần XAI.

        LƯU Ý (CP3): `beat_window` đầu vào PHẢI đã được lọc nhiễu (bandpass + notch) và
        căn theo đỉnh R + resample về 187 điểm từ trước (do `data_streamer.ecg_file_reader`
        hoặc `backend/service/diagnosis_service.py` thực hiện) — hàm này KHÔNG lọc lại vì
        sau khi resample, tần số lấy mẫu thực tế của cửa sổ không còn là 360Hz nữa (lọc lại
        ở đây bằng fs=360 sẽ sai). Ở đây chỉ chuẩn hoá biên độ về [0, 1] khớp miền dữ liệu
        Kaggle MIT-BIH đã dùng lúc train (xem plan.md mục 3.0).
        """
        if not self.is_ready or len(beat_window) != 187:
            return "CHỜ DỮ LIỆU", None, 0.0, 0.0

        t0 = time.time()

        # Chuẩn hoá biên độ về [0, 1] khớp miền dữ liệu train (lọc nhiễu đã làm trước đó)
        input_np = normalize_window(beat_window)
        # Reshape thành (batch_size=1, channels=1, seq_len=187)
        input_tensor = torch.tensor(input_np).unsqueeze(0).unsqueeze(0).to(self.device)

        # Bước 1: Predict NHANH với no_grad để lấy class + xác suất (softmax)
        with torch.no_grad():
            output = self.model(input_tensor)
            probs = torch.softmax(output, dim=1)
            pred_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_class].item()

        latency_ms = (time.time() - t0) * 1000
        
        heatmap_list = None
        
        # Bước 2: XAI (Grad-CAM) CHỈ chạy nếu phát hiện bất thường (class > 0)
        # Lần này KHÔNG dùng no_grad vì Grad-CAM cần backprop
        if pred_class > 0:
            t1 = time.time()
            # Tạo tensor mới (không dùng lại tensor cũ đã qua no_grad)
            input_tensor_xai = torch.tensor(input_np).unsqueeze(0).unsqueeze(0).to(self.device)
            cam, _ = self.gradcam.generate_heatmap(input_tensor_xai, target_class=pred_class)
            # Chuyển numpy array thành list chuẩn float để serialize sang JSON
            heatmap_list = [round(float(val), 4) for val in cam]
            latency_ms += (time.time() - t1) * 1000
            
        label_text = AAMI_CLASSES.get(pred_class, "KHÔNG XÁC ĐỊNH")

        return label_text, heatmap_list, round(latency_ms, 2), round(confidence, 4)

# Khởi tạo instance toàn cục (Singleton)
ai_service = ECGInferenceService()
