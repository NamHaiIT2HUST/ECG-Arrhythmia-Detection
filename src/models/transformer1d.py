import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """Mã hóa vị trí thời gian cho Transformer 1D."""
    def __init__(self, d_model, max_len=500):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class Transformer1D(nn.Module):
    """
    Mô hình 1D Transformer (Self-Attention):
    - Học mối tương quan phụ thuộc toàn cục trên chuỗi thời gian bằng cơ chế Tự chú ý đa đầu (Multi-Head Self-Attention).
    """
    def __init__(self, in_channels=1, seq_len=187, num_classes=5, d_model=64, nhead=4, num_layers=2, dim_feedforward=128):
        super(Transformer1D, self).__init__()
        self.embedding = nn.Linear(in_channels, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len=seq_len)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, 
            dropout=0.1, batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc1 = nn.Linear(d_model, 32)
        self.fc2 = nn.Linear(32, num_classes)

    def forward(self, x):
        if x.dim() == 2:
            x = x.unsqueeze(-1) # (batch, seq_len, 1)
        elif x.dim() == 3 and x.size(1) == 1:
            x = x.permute(0, 2, 1) # (batch, seq_len, 1)
            
        x = self.embedding(x)
        x = self.pos_encoder(x)
        
        out = self.transformer_encoder(x)
        # Pooling trên chiều thời gian
        pooled = out.mean(dim=1)
        
        h = torch.relu(self.fc1(pooled))
        logits = self.fc2(h)
        return logits
