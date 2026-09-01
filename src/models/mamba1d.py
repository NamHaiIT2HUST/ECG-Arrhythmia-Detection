import torch.nn as nn
import torch.nn.functional as F

class MambaBlock1D(nn.Module):
    """
    Khối Mamba / State Space Model (SSM) rút gọn cho 1D ECG:
    - Mô phỏng cơ chế nhớ chuỗi thời gian liên tục theo độ phức tạp tuyến tính O(N).
    - Kết hợp Gated Convolutions và State Expansion.
    """
    def __init__(self, d_model=64, d_state=16, expand=2):
        super(MambaBlock1D, self).__init__()
        self.d_inner = int(expand * d_model)
        
        self.in_proj = nn.Linear(d_model, self.d_inner * 2)
        self.conv1d = nn.Conv1d(self.d_inner, self.d_inner, kernel_size=3, padding=1, groups=self.d_inner)
        self.act = nn.SiLU()
        
        # State space linear projections
        self.x_proj = nn.Linear(self.d_inner, d_state)
        self.dt_proj = nn.Linear(d_state, self.d_inner)
        
        self.out_proj = nn.Linear(self.d_inner, d_model)

    def forward(self, x):
        # Input shape: (batch_size, seq_len, d_model)
        batch_size, seq_len, _ = x.shape
        
        xz = self.in_proj(x)
        x_proj, z = xz.chunk(2, dim=-1)
        
        # Conv1D trên chiều chuỗi (batch, d_inner, seq_len)
        x_conv = x_proj.permute(0, 2, 1)
        x_conv = self.act(self.conv1d(x_conv))
        x_conv = x_conv.permute(0, 2, 1)
        
        # State space gating logic
        ssm_state = self.x_proj(x_conv)
        dt = F.softplus(self.dt_proj(ssm_state))
        
        y = x_conv * dt * self.act(z)
        out = self.out_proj(y)
        return out

class Mamba1D(nn.Module):
    """
    Mô hình Mamba (State Space Model) cho 1D ECG:
    - Xử lý mượt mà và cực kỳ nhanh chóng trên tín hiệu sinh học với độ trễ tối thiểu.
    """
    def __init__(self, in_channels=1, seq_len=187, num_classes=5, d_model=64, num_layers=2):
        super(Mamba1D, self).__init__()
        self.embedding = nn.Linear(in_channels, d_model)
        self.layers = nn.ModuleList([MambaBlock1D(d_model=d_model) for _ in range(num_layers)])
        self.norm = nn.LayerNorm(d_model)
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):
        if x.dim() == 2:
            x = x.unsqueeze(-1)
        elif x.dim() == 3 and x.size(1) == 1:
            x = x.permute(0, 2, 1)
            
        x = self.embedding(x)
        for layer in self.layers:
            x = x + layer(x) # Residual connection
            
        x = self.norm(x)
        pooled = x.mean(dim=1)
        logits = self.fc(pooled)
        return logits
