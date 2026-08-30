import wfdb
from backend.service.inference_service import ai_service
from backend.core.signal_processing import bandpass_filter, notch_filter
from backend.core.qrs_detector import compute_all_beats

ai_service.load_model('saved_models/resnet1d.pth')

RECORD = 'data/raw/physionet_mitdb/208'
signals, fields = wfdb.rdsamp(RECORD, channels=[0])
signal = signals.flatten()
fs = fields['fs']
print(f'Record 208: {len(signal)} samples, {fs}Hz')

# CP3: lọc nhiễu + phát hiện đỉnh R (Pan-Tompkins) thay vì quét sliding-window thô,
# để mỗi cửa sổ đưa vào model là 1 nhịp tim thật đã căn đúng đỉnh R + đúng miền tần số
# đã dùng lúc train (xem plan.md mục 3.0/3.2, backend/core/qrs_detector.py).
clean = notch_filter(bandpass_filter(signal, fs=fs), fs=fs)
beats = compute_all_beats(clean, fs=fs)
print(f'Đã phát hiện {len(beats)} nhịp tim trong bản ghi.')

print('\n--- Chẩn đoán 200 nhịp đầu tiên ---')
anomaly_count = 0
normal_count = 0
for i, (r_peak_idx, window) in enumerate(beats[:200]):
    label, heatmap, latency = ai_service.predict(window)
    if 'CẢNH BÁO' in label:
        anomaly_count += 1
        if anomaly_count <= 3:
            print(f'  ANOMALY nhịp #{i} (r_peak={r_peak_idx}): {label}, heatmap_len={len(heatmap) if heatmap else 0}')
    else:
        normal_count += 1

print(f'\nKết quả: {anomaly_count} anomaly, {normal_count} normal trong 200 nhịp đầu')
print(f'Tỷ lệ phát hiện: {anomaly_count/(anomaly_count+normal_count)*100:.1f}%')
print('\n[i] Muốn kiểm tra chính xác so với nhãn bác sĩ (ground truth), chạy:')
print('    python -m backend.scripts.validate_qrs             (độ chính xác phát hiện đỉnh R)')
print('    python -m backend.scripts.validate_classification  (độ chính xác chẩn đoán end-to-end)')
