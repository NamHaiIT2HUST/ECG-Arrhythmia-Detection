from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from backend.service.diagnosis_service import parse_ecg_csv, run_offline_diagnosis
from backend.service.inference_service import ai_service

router = APIRouter()

MIN_DURATION_SECONDS = 2.0
# bandpass_filter() dùng highcut=45.0Hz mặc định - Nyquist (fs/2) phải lớn hơn 45Hz để
# scipy.signal.butter nhận tần số cắt hợp lệ (0 < Wn < 1), nên fs tối thiểu là 91Hz.
MIN_VALID_FS = 91


@router.post("/api/diagnosis/upload-ecg")
async def upload_ecg_diagnosis(
    file: UploadFile = File(...),
    fs: int = Query(360, ge=50, le=2000, description="Tần số lấy mẫu (Hz) của tín hiệu trong file"),
):
    """CP3.5: Nhận file CSV tín hiệu ECG (1 cột biên độ, có/không có header — xem
    `parse_ecg_csv`), tiền xử lý (lọc nhiễu + phát hiện đỉnh R + cắt nhịp) và chạy AI
    trên TOÀN BỘ các nhịp phát hiện được, trả về báo cáo tổng hợp (chẩn đoán offline,
    không phải luồng real-time).
    """
    if fs < MIN_VALID_FS:
        raise HTTPException(
            status_code=400,
            detail=f"fs={fs}Hz quá thấp, cần tối thiểu {MIN_VALID_FS}Hz để lọc nhiễu đúng (bộ lọc thông dải cắt tại 45Hz).",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File rỗng.")

    try:
        signal = parse_ecg_csv(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file: {e}")

    min_samples = int(fs * MIN_DURATION_SECONDS)
    if len(signal) < min_samples:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File quá ngắn hoặc không có giá trị hợp lệ nào (cần tối thiểu "
                f"{MIN_DURATION_SECONDS:.0f}s dữ liệu = {min_samples} mẫu tại fs={fs}Hz, "
                f"nhận được {len(signal)} mẫu hợp lệ)."
            ),
        )

    if not ai_service.is_ready:
        raise HTTPException(status_code=503, detail="Model AI chưa sẵn sàng, thử lại sau.")

    # run_offline_diagnosis là vòng lặp CPU-bound đồng bộ (forward + Grad-CAM cho từng nhịp),
    # có thể chạy hàng giây với file dài - chạy trong threadpool để không chặn event loop
    # dùng chung với mọi kết nối WS /ws/ecg đang stream real-time cho bệnh nhân khác.
    return await run_in_threadpool(run_offline_diagnosis, signal, fs=fs)
