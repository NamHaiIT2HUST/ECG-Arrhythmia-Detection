import asyncio
import sys
import websockets
import json

async def test_websocket(record="208", num_packets=40):
    uri = f"ws://localhost:8000/ws/ecg?record={record}"
    print(f"[+] Đang cố gắng kết nối tới {uri} ...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[✓] Kết nối thành công! Đang lắng nghe {num_packets} gói tin đầu (record={record})...\n")

            beats_seen = 0
            for i in range(num_packets):
                response = await websocket.recv()
                data = json.loads(response)

                # CP3.2/3.3: prediction/bpm/hrv chỉ THAY ĐỔI đúng lúc is_new_beat=True
                # (giữa 2 nhịp, giá trị được giữ nguyên - sample-and-hold), nên chỉ in
                # chi tiết khi có nhịp mới để log không bị lặp lại 36 lần/giây.
                if not data.get("is_new_beat"):
                    continue

                beats_seen += 1
                heatmap = data.get("heatmap")
                print(f"--- Nhịp tim mới #{beats_seen} (gói tin thứ {i+1}) ---")
                print(f"Chẩn đoán AI        : {data.get('prediction')} (độ tin cậy: {data.get('confidence')})")
                print(f"BPM tức thời        : {data.get('bpm')}")
                print(f"HRV (SDNN / RMSSD)  : {data.get('hrv_sdnn')} ms / {data.get('hrv_rmssd')} ms")
                print(f"Độ trễ AI (Latency) : {data.get('latency_ms')} ms")
                print(f"Heatmap (Grad-CAM)  : {'[Đã tạo mảng ' + str(len(heatmap)) + ' điểm]' if heatmap else 'None (nhịp bình thường)'}")
                print("-" * 30)

            print(f"\n[✓] Tổng {num_packets} gói tin, phát hiện {beats_seen} nhịp tim mới.")

    except Exception as e:
        print(f"[!] Lỗi kết nối: {e}")
        print("💡 Gợi ý: Bạn đã bật Server FastAPI chưa? Hãy chạy: .\\venv\\Scripts\\python.exe -m uvicorn backend.main:app")

if __name__ == "__main__":
    # Cho phép: python -m backend.scripts.test_ws [record_id] [so_goi_tin]
    record_arg = sys.argv[1] if len(sys.argv) > 1 else "208"
    num_packets_arg = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    asyncio.run(test_websocket(record_arg, num_packets_arg))
