from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random

app = FastAPI(title="ECG Real-time Backend")

# REACT gọi tới CROCS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên để "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/ecg")
async def ecg_stream(websocket: WebSocket):
    await websocket.accept()
    print("Khách hàng đã kết nối WebSocket!")
    try:
        while True:
            # 1. Giả lập tín hiệu ECG (Sau này thay bằng data từ cảm biến)
            is_heartbeat = random.random() > 0.9
            ecg_value = random.uniform(1.0, 3.0) if is_heartbeat else random.uniform(-0.1, 0.1)
            
            # 2. Giả lập AI dự đoán (Sau này gọi hàm model.predict() ở đây)
            prediction = "BÌNH THƯỜNG" if random.random() > 0.05 else "CẢNH BÁO: PVC"
            
            # 3. Đóng gói dữ liệu và gửi đi
            payload = {
                "value": ecg_value,
                "prediction": prediction,
                "latency_ms": random.randint(10, 15)
            }
            
            await websocket.send_json(payload)
            await asyncio.sleep(0.1)  # Tốc độ gửi: 100ms / điểm dữ liệu
            
    except Exception as e:
        print(f"Mất kết nối: {e}")