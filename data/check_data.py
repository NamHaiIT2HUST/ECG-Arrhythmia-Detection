import os
import numpy as np

# Lấy đường dẫn của thư mục hiện tại (thư mục data)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# TỰ ĐỘNG KIỂM TRA VỊ TRÍ FILE
# Trường hợp 1: File nằm trong thư mục con 'processed_data'
if os.path.exists(os.path.join(BASE_DIR, 'processed_data', 'X_train.npy')):
    DATA_PATH = os.path.join(BASE_DIR, 'processed_data')
# Trường hợp 2: File nằm ngay ngoài thư mục 'data'
elif os.path.exists(os.path.join(BASE_DIR, 'X_train.npy')):
    DATA_PATH = BASE_DIR
else:
    print("❌ LỖI: Không tìm thấy các file .npy ở đâu cả!")
    print(f"Thư mục hiện tại gồm có: {os.listdir(BASE_DIR)}")
    exit()

print("=== KIỂM TRA THÀNH PHẨM DỮ LIỆU ===")
print(f"📍 Đang đọc dữ liệu từ đường dẫn: {DATA_PATH}\n")

# Nạp dữ liệu từ đường dẫn chuẩn vừa tìm được
X_train = np.load(os.path.join(DATA_PATH, 'X_train.npy'))
y_train = np.load(os.path.join(DATA_PATH, 'y_train.npy'))
X_test = np.load(os.path.join(DATA_PATH, 'X_test.npy'))
y_test = np.load(os.path.join(DATA_PATH, 'y_test.npy'))

# 1. Kiểm tra Kích thước (Shape)
print(f"✅ Kích thước tập X_train (Dữ liệu huấn luyện): {X_train.shape}")
print(f"✅ Kích thước tập y_train (Nhãn huấn luyện):     {y_train.shape}")
print(f"✅ Kích thước tập X_test (Dữ liệu kiểm thử):    {X_test.shape}")
print(f"✅ Kích thước tập y_test (Nhãn kiểm thử):       {y_test.shape}")

print("-" * 50)

# 2. Phân phối các lớp bệnh sau khi đã chạy SMOTE
print("📊 Số lượng nhịp tim theo từng nhóm bệnh ở tập Train (sau SMOTE):")
classes, counts = np.unique(y_train, return_counts=True)
for cls, count in zip(classes, counts):
    print(f"   - Nhóm bệnh {cls}: {count} nhịp")

print("-" * 50)

# 3. Xem thử hình thù của 1 nhịp tim đầu tiên
print("📈 Biên độ sóng của nhịp tim đầu tiên (187 điểm số):")
print(X_train[0])