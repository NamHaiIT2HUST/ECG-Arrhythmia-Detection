import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/ecg"
    print(f"[+] Đang cố gắng kết nối tới {uri} ...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("[✓] Kết nối thành công! Đang lắng nghe luồng dữ liệu ECG...\n")
            
            # Chỉ nghe thử 10 gói tin đầu tiên để xem cấu trúc
            for i in range(10):
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"--- Gói tin thứ {i+1} ---")
                print(f"Dữ liệu ECG (10 điểm): {data.get('chunk')}")
                print(f"Chẩn đoán AI        : {data.get('prediction')}")
                print(f"Độ trễ AI (Latency) : {data.get('latency_ms')} ms")
                
                heatmap = data.get('heatmap')
                if heatmap:
                    print(f"Heatmap (Grad-CAM)  : [Đã tạo mảng {len(heatmap)} điểm màu đỏ]")
                else:
                    print(f"Heatmap (Grad-CAM)  : None (Nhịp bình thường, không cần vẽ)")
                print("-" * 30)
                
    except Exception as e:
        print(f"[!] Lỗi kết nối: {e}")
        print("💡 Gợi ý: Bạn đã bật Server FastAPI chưa? Hãy chạy: .\\venv\\Scripts\\python.exe -m uvicorn backend.main:app")

if __name__ == "__main__":
    asyncio.run(test_websocket())
