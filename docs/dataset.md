# Mục đích sử dụng Dataset

Dự án sử dụng kết hợp hai nguồn dữ liệu từ MIT-BIH Arrhythmia Database với các mục đích cụ thể:

* **Kaggle Dataset (`data/raw/kaggle_csv/`)**
  * **Mục đích:** Training nhanh, làm prototype (nháp) và kiểm thử tính năng của hệ thống.
  * **Lý do:** Dữ liệu đã được cộng đồng xử lý sẵn thành file CSV, giúp việc nạp dữ liệu và huấn luyện mô hình diễn ra nhanh chóng.

* **PhysioNet Dataset (`data/raw/physionet_mitdb/`)**
  * **Mục đích:** Trích xuất tín hiệu thô, lọc nhiễu và làm XAI (Grad-CAM).
  * **Lý do:** Đây là dữ liệu gốc (tín hiệu ECG liên tục). Dùng để thực hiện các bước xử lý tín hiệu chuyên sâu (lọc nhiễu, cắt nhịp) và làm cơ sở khoa học cho mô hình giải thích được (XAI) trong báo cáo cuối khóa.