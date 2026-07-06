import os
import numpy as np
import wfdb
from scipy.signal import butter, filtfilt
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# ==========================================
# 1. CẤU HÌNH THÔNG SỐ VÀ ĐƯỜNG DẪN
# ==========================================
DATA_DIR = "./raw/mit-bih-arrhythmia-database-1.0.0"     
OUTPUT_DIR = "./processed_data" # Thư mục chứa thành phẩm npy
FS = 360                      # Tần số lấy mẫu MIT-BIH
WINDOW_SIZE = 187             # Độ dài 1 nhịp tim chuẩn
HALF_WINDOW = WINDOW_SIZE // 2

# Tiêu chuẩn phân loại 5 lớp AAMI (Hiệp hội vì sự tiến bộ của Thiết bị Y tế)
AAMI_CLASSES = {'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,  # Bình thường
                'A': 1, 'a': 1, 'J': 1, 'S': 1,          # Trên thất
                'V': 2, 'E': 2,                          # Thất
                'F': 3,                                  # Hợp nhất
                '/': 4, 'f': 4, 'Q': 4}                  # Chưa phân loại

# ==========================================
# 2. HÀM LỌC NHIỄU (BUTTERWORTH BANDPASS)
# ==========================================
def butter_bandpass_filter(data, lowcut=0.5, highcut=40.0, fs=FS, order=4):
    # Khử nhiễu đường nền (<0.5Hz) và nhiễu cơ/điện (>40Hz)
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    # filtfilt giúp lọc hai chiều, không làm lệch pha hình dáng nhịp tim
    return filtfilt(b, a, data)

# ==========================================
# 3. QUY TRÌNH ĐỌC, LỌC VÀ CẮT DỮ LIỆU
# ==========================================
def process_data():
    X, y = [], []
    
    # Quét tất cả các file có đuôi .hea trong thư mục data
    if not os.path.exists(DATA_DIR):
        print(f"Lỗi: Không tìm thấy thư mục {DATA_DIR}! Hãy kiểm tra lại vị trí.")
        return None, None
        
    records = [f.split('.')[0] for f in os.listdir(DATA_DIR) if f.endswith('.hea')]
    
    if len(records) == 0:
        print("Không tìm thấy file .hea nào trong thư mục. Bạn đã giải nén chưa?")
        return None, None

    print(f"Bắt đầu dây chuyền xử lý {len(records)} bệnh nhân...")
    
    for r in records:
        path = os.path.join(DATA_DIR, r)
        try:
            # Lấy tín hiệu thô (Kênh 0 - MLII)
            signal, _ = wfdb.rdsamp(path, channels=[0])
            signal = signal.flatten()
            
            # Lấy vị trí đỉnh R do bác sĩ đánh dấu
            annotation = wfdb.rdann(path, 'atr')
            
            # BƯỚC LỌC NHIỄU
            filtered_signal = butter_bandpass_filter(signal)
            
            # BƯỚC CẮT NHỊP 187 ĐIỂM
            for idx, sample in enumerate(annotation.sample):
                label = annotation.symbol[idx]
                
                if label in AAMI_CLASSES:
                    left_bound = sample - HALF_WINDOW
                    right_bound = sample + HALF_WINDOW + 1
                    
                    # Đảm bảo nhịp cắt không bị tràn viền (out of bounds)
                    if left_bound >= 0 and right_bound <= len(filtered_signal):
                        beat = filtered_signal[left_bound:right_bound]
                        
                        if len(beat) == WINDOW_SIZE:
                            X.append(beat)
                            y.append(AAMI_CLASSES[label])
        except Exception as e:
            print(f"Bỏ qua bản ghi {r} do lỗi: {e}")
            
    return np.array(X), np.array(y)

# ==========================================
# 4. THỰC THI CHÍNH
# ==========================================
if __name__ == "__main__":
    X, y = process_data()
    
    if X is not None:
        print(f"Tổng số nhịp tim hợp lệ bóc tách được: {len(X)}")
        print(f"Phân phối các loại bệnh ban đầu: {np.bincount(y)}")
        
        # BƯỚC CHIA TRAIN/TEST (Tỷ lệ 80/20)
        # Stratify=y để đảm bảo tỷ lệ bệnh đồng đều giữa 2 tập
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # BƯỚC CÂN BẰNG DỮ LIỆU (SMOTE)
        print("Đang kích hoạt SMOTE để nhân bản nhịp tim mang bệnh...")
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        
        print(f"Phân phối sau khi cân bằng: {np.bincount(y_train_res)}")
        
        # BƯỚC XUẤT FILE NPY
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        np.save(os.path.join(OUTPUT_DIR, 'X_train.npy'), X_train_res)
        np.save(os.path.join(OUTPUT_DIR, 'y_train.npy'), y_train_res)
        np.save(os.path.join(OUTPUT_DIR, 'X_test.npy'), X_test)
        np.save(os.path.join(OUTPUT_DIR, 'y_test.npy'), y_test)
        
        print("--- THÀNH CÔNG ---")
        print(f"Nguyên liệu sạch đã được đóng gói tại thư mục: {OUTPUT_DIR}")