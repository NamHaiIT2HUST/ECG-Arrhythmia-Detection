"""
Do End-to-End Latency: tu luc phat hien 1 dinh R moi (backend/service/data_streamer.py,
truong 'detected_at') den luc payload tuong ung duoc gui qua WebSocket
(backend/api/ws_routes.py, truong 'latency_e2e_ms'). Day la con so doi chieu voi chi tieu
de cuong "End-to-End Latency < 2 giay" - xem completion_plan.md muc 3.

LUU Y 1: TestClient chay dong bo trong cung 1 tien trinh (khong qua mang that), nen so do
duoc se THAP HON thuc te khi trien khai qua mang/production - chi phan anh dung do tre
xu ly noi bo cua backend (dung Pan-Tompkins + AI + dong goi JSON), khong tinh do tre mang/
trinh duyet.

LUU Y 2: data_streamer.py co chu dich pace theo dung toc do may do that (sleep ~27.8ms/goi,
36 goi/giay), nen gom du N_BEATS nhip mat thoi gian THAT tuong duong N_BEATS nhip tim that
(vd 75bpm ~ 1.25 nhip/giay -> 200 nhip ~ 160s/ban ghi). Mac dinh N_BEATS de nho de chay
nhanh luc dev; tang len (vd 200+) khi can so lieu chinh thuc cho bao cao, chap nhan cho lau hon.

Chay: python -m backend.scripts.benchmark_e2e_latency [record_id ...]
"""
import sys

import numpy as np
from fastapi.testclient import TestClient

from backend.main import app

DEFAULT_RECORDS = ['100', '208', '234']
N_BEATS = 30  # so nhip can gom du lieu moi ban ghi (tang len vd 200 khi can so lieu chinh thuc)


def measure_record(client, record_id, n_beats=N_BEATS):
    """Mo 1 ket noi WS that toi /ws/ecg?record=<id>, gom du n_beats gia tri latency_e2e_ms
    tu cac goi tin co is_new_beat=True, tra ve mang numpy."""
    latencies = []
    with client.websocket_connect(f"/ws/ecg?record={record_id}") as ws:
        while len(latencies) < n_beats:
            data = ws.receive_json()
            if data.get("is_new_beat"):
                latencies.append(data["latency_e2e_ms"])
    return np.array(latencies)


if __name__ == "__main__":
    records = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_RECORDS

    with TestClient(app) as client:
        print(f"{'Record':<8}{'N':>6}{'Mean(ms)':>12}{'p95(ms)':>12}{'Max(ms)':>12}")
        all_latencies = []
        for rec in records:
            try:
                lat = measure_record(client, rec)
            except Exception as e:
                print(f"[!] Bỏ qua record '{rec}': {e}")
                continue
            print(f"{rec:<8}{len(lat):>6}{lat.mean():>12.2f}{np.percentile(lat, 95):>12.2f}{lat.max():>12.2f}")
            all_latencies.extend(lat.tolist())

        if all_latencies:
            all_latencies = np.array(all_latencies)
            print(f"\nTỔNG HỢP {len(records)} bản ghi: n={len(all_latencies)} "
                  f"Mean={all_latencies.mean():.2f}ms p95={np.percentile(all_latencies, 95):.2f}ms "
                  f"Max={all_latencies.max():.2f}ms")
            print("(Đo nội bộ qua TestClient, không qua mạng thật - xem docstring đầu file.)")
