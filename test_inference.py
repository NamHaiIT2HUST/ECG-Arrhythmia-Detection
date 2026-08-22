import wfdb
import numpy as np
from backend.service.inference_service import ai_service

ai_service.load_model('saved_models/resnet1d.pth')

signals, fields = wfdb.rdsamp('data/raw/physionet_mitdb/208', channels=[0])
print(f'Record 208: {len(signals)} samples, {fields["fs"]}Hz')

# Scan 10000 diem dau de tim anomaly
print('\n--- Scan record 208 tim anomaly ---')
anomaly_count = 0
normal_count = 0
for start in range(0, min(len(signals)-187, 10000), 10):
    window = signals[start:start+187].flatten().tolist()
    label, heatmap, latency = ai_service.predict(window)
    if 'CANH BAO' in label or 'CẢNH BÁO' in label:
        anomaly_count += 1
        if anomaly_count <= 3:
            print(f'  ANOMALY at start={start}: {label}, heatmap_len={len(heatmap) if heatmap else 0}')
    else:
        normal_count += 1

print(f'\nKet qua: {anomaly_count} anomaly, {normal_count} normal trong 10000 diem dau')
print(f'Ty le phat hien: {anomaly_count/(anomaly_count+normal_count)*100:.1f}%')
