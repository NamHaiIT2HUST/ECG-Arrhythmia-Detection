import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.service.data_streamer import ecg_file_reader
from backend.service.inference_service import ai_service

router = APIRouter()

# Biến cờ lưu trạng thái kết nối
active_connections = 0

@router.websocket("/ws/ecg")
async def ecg_stream_endpoint(websocket: WebSocket):
    global active_connections
    await websocket.accept()
    active_connections += 1
    print(f"[WebSocket] Client mới đã kết nối. Tổng số: {active_connections}")
    
    # Dùng data_streamer với default filepath (208 - bệnh nhân có PVC)
    # Không hardcode ở đây để data_streamer.py là nơi duy nhất kiểm soát
    ecg_stream = ecg_file_reader(chunk_size=10, fps=36)
    
    try:
        async for chunk_values, window_187 in ecg_stream:
            # 1. Gọi AI chẩn đoán trên cửa sổ 187 điểm hiện tại
            # Hàm này sẽ tự động chạy Grad-CAM nếu phát hiện bất thường
            prediction, heatmap, latency_ms = ai_service.predict(window_187)
            
            # 2. Đóng gói dữ liệu gửi về Frontend
            payload = {
                "chunk": chunk_values,         # Mảng 10 điểm để vẽ biểu đồ line liên tục
                "prediction": prediction,      # Nhãn kết quả (Ví dụ: "BÌNH THƯỜNG" hoặc "CẢNH BÁO PVC")
                "heatmap": heatmap,            # Mảng 187 màu (nếu có bệnh) hoặc None
                "latency_ms": latency_ms       # Độ trễ AI
            }
            
            await websocket.send_json(payload)
            
    except WebSocketDisconnect:
        active_connections -= 1
        print(f"[WebSocket] Client đã ngắt kết nối! Còn lại: {active_connections}")
    except Exception as e:
        print(f"[WebSocket] Lỗi luồng dữ liệu: {e}")