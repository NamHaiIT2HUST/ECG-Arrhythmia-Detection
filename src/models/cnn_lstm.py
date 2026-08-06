import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN1D_LSTM(nn.Module):
    """
    Mô hình CNN 1D + LSTM kết hợp:
    - 1D-CNN: Trích xuất đặc trưng hình thái sóng tim (Sóng P, QRS, T).
    - LSTM: Học mối quan hệ chuỗi phụ thuộc theo thời gian giữa các vùng nhịp tim.
    """
    def __init__(self, in_channels=1, num_classes=5, sequence_length=187):
        super(CNN1D_LSTM, self).__init__()
        
        # Lớp Convolutional 1D
        self.conv1 = nn.Conv1d(in_channels, 32, kernel_size=5, stride=1, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, stride=1, padding=2)
        self.bn2 = nn.BatchNorm1d(64)
        
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        
        self.pool = nn.MaxPool1d(kernel_size=2, stride=2)
        self.dropout = nn.Dropout(0.3)
        
        # Recurrent Layer (LSTM)
        # Tính toán chiều dài chuỗi sau 3 lần MaxPool (187 -> 93 -> 46 -> 23)
        self.lstm = nn.LSTM(
            input_size=128, 
            hidden_size=64, 
            num_layers=2, 
            batch_first=True, 
            bidirectional=True
        )
        
        # Lớp Phân Loại
        self.fc1 = nn.Linear(64 * 2, 64)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        # Input shape: (batch_size, 1, 187) hoặc (batch_size, 187)
        if x.dim() == 2:
            x = x.unsqueeze(1)
            
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)
        
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool(x)
        
        x = self.dropout(x)
        
        # Chuyển đổi định dạng cho LSTM: (batch_size, channels, seq_len) -> (batch_size, seq_len, channels)
        x = x.permute(0, 2, 1)
        
        lstm_out, _ = self.lstm(x)
        # Lấy hidden state ở vị trí cuối cùng của chuỗi
        last_out = lstm_out[:, -1, :]
        
        x = F.relu(self.fc1(last_out))
        x = self.dropout(x)
        logits = self.fc2(x)
        return logits
