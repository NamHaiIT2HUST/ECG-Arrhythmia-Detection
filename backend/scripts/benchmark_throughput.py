"""Đo throughput WebSocket theo kịch bản nhiều kết nối đồng thời.

Mục tiêu:
- Mỗi kết nối mở tới /ws/ecg?record=<id>
- Chạy song song với K kết nối đồng thời (K = 1, 5, 10, 20...)
- Đếm tổng số nhịp tim xử lý được trong một khoảng thời gian cố định
- Tính throughput = total_beats / elapsed_seconds
- Tính latency trung bình trên mỗi kết nối

Chạy:
    .\venv\Scripts\python.exe -m backend.scripts.benchmark_throughput
"""

import asyncio
import json
import statistics
import time
from typing import List

import websockets

RECORDS = [
    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "111", "112", "113", "114", "115", "116", "117", "118", "119", "121",
    "122", "123", "124", "200", "201", "202", "203", "205", "207", "208",
    "209", "210", "212", "213", "214", "215", "217", "219", "220", "221",
    "222", "223", "228", "230", "231", "232", "233", "234",
]

K_VALUES = [1, 5, 10, 20]
DURATION_SECONDS = 8


async def collect_stream(record_id: str, duration_seconds: float = DURATION_SECONDS):
    """Kết nối tới /ws/ecg và thống kê số beat trong khoảng thời gian nhất định."""
    uri = f"ws://localhost:8000/ws/ecg?record={record_id}"
    start = time.monotonic()
    beat_count = 0
    latencies = []

    try:
        async with websockets.connect(uri, ping_interval=None) as websocket:
            while time.monotonic() - start < duration_seconds:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                except (asyncio.TimeoutError, websockets.ConnectionClosed):
                    break

                try:
                    payload = json.loads(message)
                except json.JSONDecodeError:
                    continue

                if payload.get("is_new_beat"):
                    beat_count += 1
                    latency = payload.get("latency_ms")
                    if latency is not None:
                        try:
                            latencies.append(float(latency))
                        except (TypeError, ValueError):
                            pass
    except Exception:
        # Nếu không thể kết nối hoặc server đang tắt, trả về 0 để báo rõ kết quả.
        pass

    elapsed = max(time.monotonic() - start, 0.01)
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    return {
        "record_id": record_id,
        "beats": beat_count,
        "avg_latency_ms": avg_latency,
        "elapsed_seconds": elapsed,
    }


async def run_trial(k: int, duration_seconds: float = DURATION_SECONDS):
    """Mở K kết nối đồng thời và đo throughput tổng hợp."""
    selected_records = RECORDS[:k]
    results = await asyncio.gather(*(collect_stream(record, duration_seconds) for record in selected_records))

    total_beats = sum(item["beats"] for item in results)
    avg_latencies = [item["avg_latency_ms"] for item in results]
    elapsed_values = [item["elapsed_seconds"] for item in results]
    wall_time = max(elapsed_values) if elapsed_values else 1.0
    throughput = total_beats / wall_time if wall_time > 0 else 0.0
    mean_latency = statistics.mean(avg_latencies) if avg_latencies else 0.0

    return {
        "k": k,
        "records": selected_records,
        "total_beats": total_beats,
        "throughput_beats_per_sec": throughput,
        "avg_latency_ms": mean_latency,
        "wall_time_seconds": wall_time,
    }


async def main():
    print("Benchmark Throughput WebSocket")
    print("=" * 80)
    print(f"{ 'K':>4} | {'total_beats':>12} | {'throughput (beats/s)':>20} | {'avg_latency_ms':>16} | {'wall_time(s)':>12}")
    print("-" * 80)

    for k in K_VALUES:
        result = await run_trial(k, duration_seconds=DURATION_SECONDS)
        print(
            f"{result['k']:>4} | {result['total_beats']:>12} | {result['throughput_beats_per_sec']:>20.2f} | "
            f"{result['avg_latency_ms']:>16.2f} | {result['wall_time_seconds']:>12.2f}"
        )

    print("\nGhi chú:")
    print("- Throughput được tính trên tổng số beat xử lý trong cùng khoảng thời gian chạy đồng thời.")
    print("- latency trung bình lấy từ trung bình mỗi kết nối WebSocket.")
    print("- Nếu máy chủ chưa chạy, hãy mở terminal mới và chạy: .\\venv\\Scripts\\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    asyncio.run(main())
