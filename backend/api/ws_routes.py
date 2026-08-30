from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.service.data_streamer import ecg_file_reader
from backend.service.inference_service import ai_service
from backend.api.records_routes import record_exists, DEFAULT_RECORD

router = APIRouter()

# Biến cờ lưu trạng thái kết nối
active_connections = 0

@router.websocket("/ws/ecg")
async def ecg_stream_endpoint(websocket: WebSocket, record: str = DEFAULT_RECORD):
    global active_connections

    # CP3.4: cho phép chọn bản ghi PhysioNet muốn phát qua query param, vd:
    # ws://localhost:8000/ws/ecg?record=100  (mặc định 208 nếu không truyền)
    if not record_exists(record):
        print(f"[WebSocket] Record '{record}' không tồn tại, dùng mặc định '{DEFAULT_RECORD}'.")
        record = DEFAULT_RECORD

    await websocket.accept()
    active_connections += 1
    print(f"[WebSocket] Client mới đã kết nối (record={record}). Tổng số: {active_connections}")

    filepath = f"data/raw/physionet_mitdb/{record}"
    ecg_stream = ecg_file_reader(filepath=filepath, chunk_size=10, fps=36)

    # CP3.2/3.3: AI + BPM/HRV giờ chỉ được tính LẠI mỗi khi có 1 nhịp tim mới (đỉnh R),
    # không còn chạy trên mọi gói tin. Giữ nguyên giá trị gần nhất (sample-and-hold)
    # giữa 2 nhịp để Dashboard luôn có dữ liệu hiển thị, không bị chớp về rỗng.
    last_prediction = "CHỜ DỮ LIỆU"
    last_latency_ms = 0.0
    last_bpm = 0.0
    last_hrv_sdnn = 0.0
    last_hrv_rmssd = 0.0

    try:
        async for chunk_values, beat_info in ecg_stream:
            heatmap = None

            if beat_info is not None:
                # 1 nhịp tim mới vừa được cắt theo đỉnh R -> chạy AI đúng 1 lần cho nhịp này
                # (predict() sẽ tự chạy Grad-CAM nếu phát hiện bất thường)
                last_prediction, heatmap, last_latency_ms = ai_service.predict(beat_info["window"])
                last_bpm = beat_info["bpm"]
                last_hrv_sdnn = beat_info["hrv_sdnn"]
                last_hrv_rmssd = beat_info["hrv_rmssd"]

            # 2. Đóng gói dữ liệu gửi về Frontend
            payload = {
                "chunk": chunk_values,         # Mảng 10 điểm (đã lọc nhiễu) để vẽ biểu đồ line liên tục
                "prediction": last_prediction, # Nhãn kết quả nhịp gần nhất (giữ nguyên tới khi có nhịp mới)
                "heatmap": heatmap,            # Mảng 187 màu CHỈ có ở đúng gói tin phát hiện nhịp mới, còn lại None
                "latency_ms": last_latency_ms, # Độ trễ AI của lần chẩn đoán gần nhất
                "bpm": last_bpm,                # Nhịp tim tức thời (BPM) theo khoảng RR thực tế
                "hrv_sdnn": last_hrv_sdnn,      # HRV - SDNN (ms), cửa sổ trượt tối đa 50 nhịp gần nhất
                "hrv_rmssd": last_hrv_rmssd,    # HRV - RMSSD (ms)
                "is_new_beat": beat_info is not None,  # true đúng lúc vừa chẩn đoán 1 nhịp mới
            }

            await websocket.send_json(payload)

    except WebSocketDisconnect:
        active_connections -= 1
        print(f"[WebSocket] Client đã ngắt kết nối! Còn lại: {active_connections}")
    except Exception as e:
        print(f"[WebSocket] Lỗi luồng dữ liệu: {e}")