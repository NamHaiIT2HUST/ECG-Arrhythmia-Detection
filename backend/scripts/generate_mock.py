import csv
import math
import os

# Tạo thư mục data nếu chưa có
os.makedirs("data", exist_ok=True)

filepath = "data/mock_ecg.csv"

# Tạo 1000 dòng dữ liệu hình sin giả lập sóng tim
with open(filepath, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "value"]) # Header
    for i in range(1000):
        # Sóng cơ bản + thỉnh thoảng có đỉnh nhọn
        val = math.sin(i * 0.1) + (2.5 if i % 10 == 0 else 0)
        writer.writerow([i, round(val, 3)])

print(f"Đã tạo xong file {filepath}!")