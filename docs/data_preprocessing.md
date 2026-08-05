# Báo Cáo: Tiền xử lý dữ liệu (Data Preprocessing)

**Mục tiêu:** Xử lý và chuẩn hóa dữ liệu tín hiệu điện tâm đồ (ECG) từ dạng thô thành các mảng vector (Numpy Arrays) đã được cân bằng, sẵn sàng cho việc huấn luyện các mô hình Deep Learning.

## 1. Đầu vào (Input)

Dữ liệu đầu vào được lấy từ bộ dữ liệu **MIT-BIH Arrhythmia Dataset** (thông qua Kaggle CSV), được đặt trong thư mục `data/raw/kaggle_csv/`:
- `mitbih_train.csv`: 87,554 mẫu nhịp tim.
- `mitbih_test.csv`: 21,892 mẫu nhịp tim.

Mỗi mẫu nhịp tim là một chuỗi thời gian (time-series) gồm **187 điểm dữ liệu** (đã được trích xuất với cửa sổ độ rộng chuẩn) và 1 nhãn lớp ở cột cuối cùng.

**Các lớp phân loại (AAMI Classes):**
- `0`: Nhịp bình thường (Normal - N)
- `1`: Nhịp trên thất (Supraventricular ectopic - S)
- `2`: Nhịp thất (Ventricular ectopic - V)
- `3`: Nhịp hợp nhất (Fusion - F)
- `4`: Nhịp chưa phân loại (Unknown - Q)

*Lưu ý: Dữ liệu gốc gặp phải tình trạng mất cân bằng trầm trọng (Imbalanced Data), với nhịp bình thường (lớp 0) chiếm hơn 82%, trong khi các lớp bất thường chiếm tỷ lệ rất nhỏ.*

## 2. Các bước xử lý (Processing Steps)

Quá trình tiền xử lý được thực thi trong file [`data/preprocess.py`](../data/preprocess.py) với các bước sau:

1. **Đọc dữ liệu:** Nạp dữ liệu từ các file CSV thành các ma trận Numpy.
2. **Phân tách Features và Labels:** Tách 187 cột đầu thành tập tín hiệu (X), và cột cuối cùng thành tập nhãn (y).
3. **Cân bằng dữ liệu bằng thuật toán SMOTE (Synthetic Minority Over-sampling Technique):** 
   - Vì lớp 0 áp đảo hoàn toàn các lớp khác, mô hình AI nếu train trực tiếp sẽ bị "thiên vị" (bias) dẫn tới dự đoán lúc nào cũng là lớp 0.
   - SMOTE được áp dụng trên tập Train nhằm sinh ra các mẫu nhân tạo (synthetic samples) cho các nhóm thiểu số (Lớp 1, 2, 3, 4) dựa trên nội suy từ các lân cận gần nhất (K-Nearest Neighbors).
   - *Kết quả:* Tất cả 5 lớp trong tập Train đều được cân bằng về cùng số lượng mẫu (72,471 mẫu cho mỗi lớp).

## 3. Đầu ra (Output)

Dữ liệu sau khi xử lý được đóng gói thành các file `.npy` (Numpy Binary) và lưu tại thư mục `data/processed/` để tăng tốc độ nạp (I/O) khi huấn luyện AI:

- `X_train_kaggle.npy`: Ma trận tín hiệu huấn luyện (đã cân bằng).
- `y_train_kaggle.npy`: Nhãn của tập huấn luyện (đã cân bằng).
- `X_test_kaggle.npy`: Ma trận tín hiệu kiểm thử (giữ nguyên tỷ lệ thực tế, không dùng SMOTE).
- `y_test_kaggle.npy`: Nhãn của tập kiểm thử.

Các file đầu ra này đã sẵn sàng để được nạp vào luồng xử lý (Data Loader) của PyTorch trong Bước 2.
