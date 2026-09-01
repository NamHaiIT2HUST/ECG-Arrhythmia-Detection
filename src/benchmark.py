import os
import sys
import time
import json
import argparse
import glob
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from models import CNN1D_LSTM, TemporalConvNet, ResNet1D, Transformer1D, Mamba1D

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 128
EPOCHS = 10
LEARNING_RATE = 1e-3

def load_data(dataset_type="kaggle"):
    """Nạp dữ liệu đã xử lý từ data/processed/"""
    if dataset_type == "kaggle":
        x_tr_path = os.path.join(PROCESSED_DIR, "X_train_kaggle.npy")
        y_tr_path = os.path.join(PROCESSED_DIR, "y_train_kaggle.npy")
        x_te_path = os.path.join(PROCESSED_DIR, "X_test_kaggle.npy")
        y_te_path = os.path.join(PROCESSED_DIR, "y_test_kaggle.npy")
    else:
        x_tr_path = os.path.join(PROCESSED_DIR, "X_train_physio.npy")
        y_tr_path = os.path.join(PROCESSED_DIR, "y_train_physio.npy")
        x_te_path = os.path.join(PROCESSED_DIR, "X_test_physio.npy")
        y_te_path = os.path.join(PROCESSED_DIR, "y_test_physio.npy")
        
    if not os.path.exists(x_tr_path):
        raise FileNotFoundError(f"Chưa tìm thấy dữ liệu {x_tr_path}! Hãy chạy 'python data/preprocess.py' trước.")
        
    X_train = np.load(x_tr_path)
    y_train = np.load(y_tr_path)
    X_test = np.load(x_te_path)
    y_test = np.load(y_te_path)

    return X_train, y_train, X_test, y_test

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def train_and_eval_model(model_name, model, train_loader, test_loader, num_classes=5):
    print("\n==================================================")
    print(f" 🚀 ĐANG TRAIN & BÁO CÁO: {model_name}")
    print("==================================================")
    print(f"[i] Thiết bị: {DEVICE} | Số lượng tham số: {count_parameters(model):,}")
    
    model = model.to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Quá trình Huấn Luyện
    model.train()
    start_train_time = time.time()
    for epoch in range(EPOCHS):
        total_loss = 0.0
        for i, (batch_x, batch_y) in enumerate(train_loader):
            batch_x, batch_y = batch_x.to(DEVICE), batch_y.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
            # In tiến trình mỗi 100 batch (dùng \r để ghi đè trên cùng 1 dòng)
            if (i + 1) % 100 == 0 or (i + 1) == len(train_loader):
                print(f"   [Epoch {epoch+1}/{EPOCHS}] Batch {i+1}/{len(train_loader)} - Loss: {loss.item():.4f}", end='\r')
                
        print(f"\n[✓] Epoch [{epoch+1}/{EPOCHS}] Hoàn thành - Avg Loss: {total_loss/len(train_loader):.4f}")
        
    train_duration = time.time() - start_train_time
    print(f"[✓] Hoàn thành huấn luyện trong: {train_duration:.2f}s")
    
    # Quá trình Đánh Giá (Inference & Real-time Metrics)
    model.eval()
    all_preds = []
    all_targets = []
    
    inference_times = []
    
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(DEVICE)
            
            t0 = time.time()
            outputs = model(batch_x)
            t1 = time.time()
            
            # Thời gian tính toán cho 1 sample (ms)
            sample_time_ms = ((t1 - t0) / batch_x.size(0)) * 1000.0
            inference_times.append(sample_time_ms)
            
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(batch_y.numpy())
            
    avg_latency = float(np.mean(inference_times))
    throughput = float(1000.0 / avg_latency) if avg_latency > 0 else 0.0
    
    acc = float(accuracy_score(all_targets, all_preds))
    prec, rec, f1, _ = precision_recall_fscore_support(all_targets, all_preds, average='macro')
    
    print("\n--- KẾT QUẢ ĐỐI SÁNH HIỆU NĂNG ---")
    print(f"• Accuracy : {acc * 100:.2f}%")
    print(f"• Precision: {float(prec) * 100:.2f}%")
    print(f"• Recall    : {float(rec) * 100:.2f}% (Độ bao phủ phát hiện bệnh)")
    print(f"• F1-Score  : {float(f1) * 100:.2f}%")
    print(f"• Latency   : {avg_latency:.4f} ms/sample (Thời gian suy luận)")
    print(f"• Throughput: {throughput:.0f} samples/sec")
    
    # Lưu trọng số mô hình tốt nhất
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    save_path = os.path.join(SAVED_MODELS_DIR, f"{model_name.lower().replace(' ', '_')}.pth")
    torch.save(model.state_dict(), save_path)
    print(f"[✓] Đã lưu trọng số mô hình vào {save_path}")
    
    return {
        "Model": model_name,
        "Accuracy (%)": round(acc * 100, 2),
        "Precision (%)": round(float(prec) * 100, 2),
        "Recall (%)": round(float(rec) * 100, 2),
        "F1-Score (%)": round(float(f1) * 100, 2),
        "Inference Latency (ms)": round(avg_latency, 4),
        "Throughput (samples/s)": round(throughput, 0),
        "Parameters": count_parameters(model),
        "Train Duration (s)": round(train_duration, 2)
    }

def save_benchmark_reports(results):
    """Xuất kết quả đối sánh ra CSV, JSON và Markdown"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    df = pd.DataFrame(results)
    
    # 1. Lưu CSV
    csv_path = os.path.join(DOCS_DIR, "benchmark_results.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    # 2. Lưu JSON
    json_path = os.path.join(DOCS_DIR, "benchmark_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    # 3. Báo cáo Markdown
    md_path = os.path.join(DOCS_DIR, "benchmark_results.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Báo Cáo Đối Sánh Hiệu Năng 5 Mô Hình Deep Learning (ECG Arrhythmia)\n\n")
        f.write(f"**Ngày nghiệm thu**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n\n---\n*Báo cáo được khởi tạo tự động bởi benchmark suite.*")
        
    print("\n==================================================")
    print(" 💾 ĐÃ LƯU BÁO CÁO KẾT QUẢ ĐỐI SÁNH TỰ ĐỘNG:")
    print(f" • CSV     : {csv_path}")
    print(f" • JSON    : {json_path}")
    print(f" • Markdown: {md_path}")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark ECG Models")
    parser.add_argument("--model", type=str, help="Tên model cần train (VD: CNN1D_LSTM, TCN, ResNet1D, Transformer1D, Mamba1D)", default=None)
    parser.add_argument("--aggregate", action="store_true", help="Tổng hợp kết quả từ các file temp_*.json")
    args = parser.parse_args()

    if args.aggregate:
        print("[+] Đang tổng hợp kết quả...")
        temp_files = glob.glob(os.path.join(DOCS_DIR, "temp_result_*.json"))
        if not temp_files:
            print("[!] Không tìm thấy kết quả nào để tổng hợp.")
            sys.exit(0)
            
        results = []
        for f in temp_files:
            with open(f, 'r', encoding='utf-8') as file:
                results.append(json.load(file))
                
        save_benchmark_reports(results)
        
        # Xóa các file tạm sau khi tổng hợp xong
        for f in temp_files:
            os.remove(f)
        sys.exit(0)

    # Nếu không phải aggregate thì load data để train
    try:
        X_tr, y_tr, X_te, y_te = load_data("kaggle")
    except Exception as e:
        print(f"[!] {e}")
        sys.exit(1)
        
    train_dataset = TensorDataset(torch.tensor(X_tr, dtype=torch.float32), torch.tensor(y_tr, dtype=torch.long))
    test_dataset = TensorDataset(torch.tensor(X_te, dtype=torch.float32), torch.tensor(y_te, dtype=torch.long))
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    candidate_models = {
        "CNN1D_LSTM": CNN1D_LSTM,
        "TCN": TemporalConvNet,
        "ResNet1D": ResNet1D,
        "Transformer1D": Transformer1D,
        "Mamba1D": Mamba1D
    }
    
    if args.model:
        if args.model not in candidate_models:
            print(f"[!] Tên model '{args.model}' không hợp lệ. Chọn 1 trong: {list(candidate_models.keys())}")
            sys.exit(1)
            
        print(f"[+] Bắt đầu train duy nhất model: {args.model}")
        model_instance = candidate_models[args.model]()
        res = train_and_eval_model(args.model, model_instance, train_loader, test_loader)
        
        # Lưu kết quả tạm thời
        os.makedirs(DOCS_DIR, exist_ok=True)
        temp_path = os.path.join(DOCS_DIR, f"temp_result_{args.model}.json")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
        print(f"[✓] Đã lưu kết quả tạm vào {temp_path}")
        print(f"    (Chạy các model khác, sau đó dùng cờ --aggregate để tổng hợp)")
        
    else:
        print("[+] Không chỉ định --model. Sẽ train toàn bộ 5 model liên tục...")
        results = []
        for name, ModelClass in candidate_models.items():
            model_instance = ModelClass()
            res = train_and_eval_model(name, model_instance, train_loader, test_loader)
            results.append(res)
            
        save_benchmark_reports(results)
