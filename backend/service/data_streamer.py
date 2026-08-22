import os
import asyncio
import wfdb
import numpy as np
from collections import deque

# Resolve đường dẫn tuyệt đối từ vị trí file này
# Tránh bị lỗi khi chạy uvicorn từ thư mục khác
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bộ đệm để chứa 187 điểm liên tiếp cho AI dự đoán
ecg_buffer = deque(maxlen=187)

async def ecg_file_reader(filepath="data/raw/physionet_mitdb/208", chunk_size=10, fps=36):
    """
    Giả lập máy điện tim đọc liên tục từ file tín hiệu PhysioNet.
    - chunk_size: Gửi bao nhiêu điểm trong 1 gói tin (mặc định 10 điểm).
    - fps: Tốc độ gửi gói tin (36 lần/giây x 10 điểm = 360 điểm/giây, bằng đúng tần số chuẩn của MIT-BIH).
    """
    # Delay cho mỗi vòng lặp để mô phỏng real-time
    delay_s = 1.0 / fps
    
    # Resolve đường dẫn tuyệt đối để tránh lỗi khi chạy từ thư mục khác
    abs_filepath = os.path.join(BASE_DIR, filepath) if not os.path.isabs(filepath) else filepath
    
    if not os.path.exists(abs_filepath + ".dat"):
        print(f"[!] Không tìm thấy file gốc {abs_filepath}.dat. Vui lòng tải data MIT-BIH trước.")
        # Fallback tạo data nhiễu
        while True:
            yield [0.0]*chunk_size, list(ecg_buffer)
            await asyncio.sleep(delay_s)

    # Dùng wfdb đọc toàn bộ tín hiệu của kênh 0 (MLII)
    try:
        signals, fields = wfdb.rdsamp(abs_filepath, channels=[0])
        signals = signals.flatten()
    except Exception as e:
        print(f"[!] Lỗi đọc wfdb: {e}")
        return

    print(f"[+] Bắt đầu phát sóng stream ({fps} FPS), tổng {len(signals)} điểm...")
    
    # Khởi tạo buffer bằng các giá trị đầu tiên cho đầy 187 điểm
    for i in range(187):
        ecg_buffer.append(float(signals[i]))

    # Bắt đầu phát luồng từ điểm 187 trở đi
    idx = 187
    while True:
        chunk = []
        for _ in range(chunk_size):
            if idx >= len(signals):
                idx = 0 # Loop lại từ đầu để demo chạy mãi mãi
                
            val = float(signals[idx])
            chunk.append(val)
            ecg_buffer.append(val)
            idx += 1
            
        # Trả về: (Dữ liệu 10 điểm mới để vẽ, Toàn bộ 187 điểm hiện tại để AI chẩn đoán)
        yield chunk, list(ecg_buffer)
        
        await asyncio.sleep(delay_s)