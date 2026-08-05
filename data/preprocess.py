import os
import pandas as pd
import numpy as np
import wfdb
from scipy.signal import butter, filtfilt
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

# ==========================================
# 1. CẤU HÌNH THÔNG SỐ VÀ ĐƯỜNG DẪN
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHYSIONET_DIR = os.path.join(BASE_DIR, "raw", "physionet_mitdb")
KAGGLE_DIR = os.path.join(BASE_DIR, "raw", "kaggle_csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "processed")

FS = 360                      # Tần số lấy mẫu MIT-BIH (Hz)
WINDOW_SIZE = 187             # Độ dài chuẩn cho 1 nhịp tim
HALF_WINDOW = WINDOW_SIZE // 2

# Tiêu chuẩn phân loại 5 lớp AAMI
AAMI_CLASSES = {
    'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,  # Nhóm N: Bình thường (Normal)
    'A': 1, 'a': 1, 'J': 1, 'S': 1,          # Nhóm S: Trên thất (Supraventricular)
    'V': 2, 'E': 2,                          # Nhóm V: Thất / PVC (Ventricular)
    'F': 3,                                  # Nhóm F: Hợp nhất (Fusion)
    '/': 4, 'f': 4, 'Q': 4                   # Nhóm Q: Chưa phân loại (Unclassifiable)
}

# ==========================================
# 2. HÀM LỌC NHIỄU (BUTTERWORTH BANDPASS)
# ==========================================
def butter_bandpass_filter(data, lowcut=0.5, highcut=40.0, fs=FS, order=4):
    """Lọc băng thông Butterworth (0.5 - 40Hz) loại bỏ nhiễu đường nền và nhiễu cơ."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

# ==========================================
# 3. QUY TRÌNH XỬ LÝ DỮ LIỆU PHYSIONET WFDB
# ==========================================
def process_physionet_data():
    """Trích xuất và lọc tín hiệu thô từ bộ dữ liệu PhysioNet MIT-BIH."""
    X, y = [], []
    
    if not os.path.exists(PHYSIONET_DIR):
        print(f"[!] Lỗi: Không tìm thấy thư mục {PHYSIONET_DIR}")
        return None, None
        
    records = [f.split('.')[0] for f in os.listdir(PHYSIONET_DIR) if f.endswith('.hea')]
    records = sorted(list(set(records)))
    
    if len(records) == 0:
        print(f"[!] Không tìm thấy file .hea trong {PHYSIONET_DIR}")
        return None, None

    print(f"[+] Bắt đầu trích xuất tín hiệu từ {len(records)} hồ sơ bệnh nhân PhysioNet...")
    
    for r in records:
        path = os.path.join(PHYSIONET_DIR, r)
        try:
            # Lấy tín hiệu thô (Kênh MLII)
            signal, _ = wfdb.rdsamp(path, channels=[0])
            signal = signal.flatten()
            
            # Đọc nhãn đỉnh R do bác sĩ đánh dấu
            annotation = wfdb.rdann(path, 'atr')
            
            # Lọc nhiễu tín hiệu
            filtered_signal = butter_bandpass_filter(signal)
            
            # Bóc tách cửa sổ 187 điểm quanh đỉnh R
            for idx, sample in enumerate(annotation.sample):
                label = annotation.symbol[idx]
                
                if label in AAMI_CLASSES:
                    left_bound = sample - HALF_WINDOW
                    right_bound = sample + HALF_WINDOW + 1
                    
                    if left_bound >= 0 and right_bound <= len(filtered_signal):
                        beat = filtered_signal[left_bound:right_bound]
                        if len(beat) == WINDOW_SIZE:
                            X.append(beat)
                            y.append(AAMI_CLASSES[label])
        except Exception as e:
            print(f"[!] Bỏ qua bản ghi {r}: {e}")
            
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)

# ==========================================
# 4. QUY TRÌNH XỬ LÝ DỮ LIỆU KAGGLE CSV
# ==========================================
def process_kaggle_csv():
    """Đọc dữ liệu đã cắt sẵn từ các file CSV của Kaggle (mitbih_train & mitbih_test)."""
    train_path = os.path.join(KAGGLE_DIR, "mitbih_train.csv")
    test_path = os.path.join(KAGGLE_DIR, "mitbih_test.csv")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print(f"[!] Không tìm thấy file Kaggle CSV tại {KAGGLE_DIR}")
        return None, None, None, None
        
    print("[+] Đang tải dữ liệu Kaggle CSV (mitbih_train & mitbih_test)...")
    df_train = pd.read_csv(train_path, header=None)
    df_test = pd.read_csv(test_path, header=None)
    
    X_train = df_train.iloc[:, :-1].values.astype(np.float32)
    y_train = df_train.iloc[:, -1].values.astype(np.int64)
    
    X_test = df_test.iloc[:, :-1].values.astype(np.float32)
    y_test = df_test.iloc[:, -1].values.astype(np.int64)
    
    return X_train, y_train, X_test, y_test

# ==========================================
# 5. LỒNG GHÉP THỰC THI CHÍNH
# ==========================================
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("==================================================")
    print("  BƯỚC 1: XỬ LÝ & ĐÓNG GÓI DỮ LIỆU TÍN HIỆU ECG")
    print("==================================================")
    
    # 1. Thử nghiệm trích xuất PhysioNet (Tín hiệu thô trực tiếp)
    X_physio, y_physio = process_physionet_data()
    
    if X_physio is not None and len(X_physio) > 0:
        print(f"[✓] PhysioNet: Trích xuất thành công {len(X_physio)} nhịp tim.")
        print(f"    Phân phối các lớp ban đầu: {np.bincount(y_physio)}")
        
        # Chia tập Train (80%) và Test (20%)
        X_train, X_test, y_train, y_test = train_test_split(
            X_physio, y_physio, test_size=0.2, random_state=42, stratify=y_physio
        )
        
        # Cân bằng dữ liệu tập Train bằng SMOTE
        print("[+] Đang thực hiện cân bằng dữ liệu (SMOTE) cho PhysioNet...")
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        print(f"    Phân phối sau SMOTE: {np.bincount(y_train_res)}")
        
        # Lưu file PhysioNet
        np.save(os.path.join(OUTPUT_DIR, 'X_train_physio.npy'), X_train_res)
        np.save(os.path.join(OUTPUT_DIR, 'y_train_physio.npy'), y_train_res)
        np.save(os.path.join(OUTPUT_DIR, 'X_test_physio.npy'), X_test)
        np.save(os.path.join(OUTPUT_DIR, 'y_test_physio.npy'), y_test)
        print("[✓] Đã lưu dữ liệu PhysioNet đã xử lý vào data/processed/")

    # 2. Xử lý dữ liệu Kaggle CSV
    X_tr_k, y_tr_k, X_te_k, y_te_k = process_kaggle_csv()
    if X_tr_k is not None:
        print(f"[✓] Kaggle CSV: Đã nạp {len(X_tr_k)} mẫu train và {len(X_te_k)} mẫu test.")
        print(f"    Phân phối tập train Kaggle: {np.bincount(y_tr_k)}")
        
        # Cân bằng dữ liệu Kaggle bằng SMOTE
        print("[+] Đang thực hiện cân bằng dữ liệu (SMOTE) cho Kaggle CSV...")
        smote_k = SMOTE(random_state=42)
        X_tr_k_res, y_tr_k_res = smote_k.fit_resample(X_tr_k, y_tr_k)
        print(f"    Phân phối sau SMOTE: {np.bincount(y_tr_k_res)}")
        
        # Lưu file Kaggle CSV
        np.save(os.path.join(OUTPUT_DIR, 'X_train_kaggle.npy'), X_tr_k_res)
        np.save(os.path.join(OUTPUT_DIR, 'y_train_kaggle.npy'), y_tr_k_res)
        np.save(os.path.join(OUTPUT_DIR, 'X_test_kaggle.npy'), X_te_k)
        np.save(os.path.join(OUTPUT_DIR, 'y_test_kaggle.npy'), y_te_k)
        print("[✓] Đã lưu dữ liệu Kaggle CSV đã xử lý vào data/processed/")
        
    print("==================================================")
    print("  HOÀN THÀNH BƯỚC 1: DỮ LIỆU ĐÃ SẴN SÀNG TRAIN!")
    print("==================================================")