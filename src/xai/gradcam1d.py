import torch
import torch.nn.functional as F
import numpy as np

class GradCAM1D:
    """
    1D Grad-CAM (Gradient-weighted Class Activation Mapping) cho tín hiệu ECG 1 chiều:
    - Trực quan hóa mức độ quan trọng (heatmap) của từng đoạn sóng ECG (Sóng P, QRS, T)
      đối với quyết định chẩn đoán của mô hình AI.
    """
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Đăng ký Hook lấy gradient và activation
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, input_tensor, target_class=None):
        """
        Tạo mảng Heatmap 1D chuẩn hóa [0, 1] có chiều dài bằng với input ECG.
        """
        self.model.eval()
        self.model.zero_grad()
        
        if input_tensor.dim() == 2:
            input_tensor = input_tensor.unsqueeze(1)
            
        input_tensor.requires_grad = True
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        score = output[0, target_class]
        score.backward()
        
        gradients = self.gradients.data[0] # Shape: (channels, seq_len)
        activations = self.activations.data[0] # Shape: (channels, seq_len)
        
        # Global Average Pooling trên các gradient để lấy trọng số alpha
        weights = torch.mean(gradients, dim=1, keepdim=True)
        
        # Nhân trọng số với activations
        cam = torch.sum(weights * activations, dim=0)
        cam = F.relu(cam) # Chỉ lấy các đóng góp tích cực (ReLU)
        
        # Interpolate về chiều dài ban đầu của tín hiệu ECG (vd: 187 points)
        cam = cam.unsqueeze(0).unsqueeze(0)
        cam = F.interpolate(cam, size=input_tensor.size(-1), mode='linear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        
        # Chuẩn hóa về dải [0, 1] - dùng ngưỡng epsilon (không so sánh != 0 tuyệt đối, cùng lý
        # do với signal_processing.normalize_window) để tránh khuếch đại nhiễu dấu phẩy động
        # thành heatmap dao động toàn dải [0,1] khi vùng activation gần như đồng đều.
        cam_range = np.max(cam) - np.min(cam)
        if cam_range > 1e-8:
            cam = (cam - np.min(cam)) / cam_range
        else:
            cam = np.zeros_like(cam)
            
        return cam, target_class


class Saliency1D:
    """
    1D Saliency Maps (Gradient x Input) cho tín hiệu ECG 1 chiều:
    - Tính đạo hàm trực tiếp của output so với input đầu vào.
    - Cực kỳ nhanh do không cần hook vào các lớp ẩn.
    """
    def __init__(self, model):
        self.model = model

    def generate_heatmap(self, input_tensor, target_class=None):
        self.model.eval()
        self.model.zero_grad()
        
        if input_tensor.dim() == 2:
            input_tensor = input_tensor.unsqueeze(1)
            
        input_tensor.requires_grad = True
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = torch.argmax(output, dim=1).item()
            
        score = output[0, target_class]
        score.backward()
        
        # Lấy gradient tại input
        gradients = input_tensor.grad.data.abs().squeeze().cpu().numpy()
        input_data = input_tensor.data.abs().squeeze().cpu().numpy()
        
        # Gradient x Input
        saliency = gradients * input_data
        
        # Chuẩn hóa về dải [0, 1] - epsilon thay vì != 0 tuyệt đối, cùng lý do như GradCAM1D ở trên.
        saliency_range = np.max(saliency) - np.min(saliency)
        if saliency_range > 1e-8:
            saliency = (saliency - np.min(saliency)) / saliency_range
        else:
            saliency = np.zeros_like(saliency)
            
        return saliency, target_class
