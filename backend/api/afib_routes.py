from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool

from backend.service.afib_screening_service import screen_afib_signal
from backend.service.diagnosis_service import parse_ecg_csv

router = APIRouter()

MIN_DURATION_SECONDS = 2.0
MIN_VALID_FS = 91


@router.post("/api/screening/afib")
async def screening_afib(
    file: UploadFile = File(...),
    fs: int = Query(360, ge=50, le=2000, description="Tần số lấy mẫu (Hz) của tín hiệu ECG."),
):
    """Sàng lọc rung nhĩ (AFib) trên một đoạn ECG tải lên.

    Endpoint này không thay thế chẩn đoán lâm sàng, nhưng là một lớp screening nhanh
    dựa trên:
    - độ không đều của RR interval
    - tần số tim
    - khả năng thiếu P-wave
    - threshold đã hiệu chỉnh theo AFDB nếu có dữ liệu mẫu. 
    """
    if fs < MIN_VALID_FS:
        raise HTTPException(
            status_code=400,
            detail=f"fs={fs}Hz quá thấp, cần tối thiểu {MIN_VALID_FS}Hz để phát hiện R-peak và HRV hợp lệ.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File rỗng.")

    try:
        signal = parse_ecg_csv(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không đọc được file: {e}") from e

    min_samples = int(fs * MIN_DURATION_SECONDS)
    if len(signal) < min_samples:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File quá ngắn hoặc không có dữ liệu hợp lệ (cần tối thiểu "
                f"{MIN_DURATION_SECONDS:.0f}s = {min_samples} mẫu tại fs={fs}Hz; "
                f"nhận được {len(signal)} mẫu)."
            ),
        )

    return await run_in_threadpool(screen_afib_signal, signal, fs=fs)
