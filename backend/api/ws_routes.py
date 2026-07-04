from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.data_streamer import ecg_file_reader
import random

router = APIRouter()

@router.websocket("/ws/ecg")
async def ecg_stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Khởi tạo luồng đọc file
    ecg_stream = ecg_file_reader(filepath="data/mock_ecg.csv", delay_ms=100)
    
    try:
        async for value in ecg_stream:
            # Chỗ này sau này cắm Model AI vào: prediction = model.predict(value)
            prediction = "BÌNH THƯỜNG" if random.random() > 0.05 else "CẢNH BÁO PVC"
            
            payload = {
                "value": value,
                "prediction": prediction,
                "latency_ms": random.randint(5, 15)
            }
            await websocket.send_json(payload)
            
    except WebSocketDisconnect:
        print("Client đã ngắt kết nối!")