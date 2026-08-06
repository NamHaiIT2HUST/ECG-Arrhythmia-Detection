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
        
        # Chuẩn hóa về dải [0, 1]
        if np.max(cam) - np.min(cam) != 0:
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam))
        else:
            cam = np.zeros_like(cam)
            
        return cam, target_class
