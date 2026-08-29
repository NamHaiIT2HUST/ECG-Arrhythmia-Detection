import os
from fastapi import APIRouter

router = APIRouter()

DEFAULT_RECORD = "208"
PHYSIONET_DIR = os.path.join("data", "raw", "physionet_mitdb")

# Mô tả lâm sàng cho các bản ghi tiêu biểu hay dùng để demo (xem plan.md mục 3.2).
# Bản ghi nào không có trong danh sách này vẫn liệt kê được, chỉ dùng mô tả mặc định.
CURATED_DESCRIPTIONS = {
    "100": "Nhịp xoang bình thường - phù hợp demo baseline",
    "119": "Ngoại tâm thu thất (PVC) tần suất cao",
    "200": "Ngoại tâm thu thất (PVC) dạng đôi + nhịp nhanh thất từng đợt",
    "207": "Rung thất / Cuồng nhĩ - loạn nhịp nguy hiểm, khó phát hiện đỉnh R",
    "208": "Ngoại tâm thu thất (PVC) tần suất rất cao (mặc định khi stream)",
    "213": "Ngoại tâm thu nhĩ (PAC) + ngoại tâm thu thất xen kẽ",
    "217": "Nhịp máy tạo nhịp (paced beats) + ngoại tâm thu thất",
    "234": "Nhịp xoang bình thường kèm vài nhịp trên thất (SVT)",
}


def _abs_physio_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, PHYSIONET_DIR)


def list_available_records():
    """Quét thư mục data/raw/physionet_mitdb/ tìm các bản ghi có đủ cặp file .hea + .dat."""
    physio_dir = _abs_physio_dir()
    if not os.path.isdir(physio_dir):
        return []

    record_ids = sorted({
        f[:-4] for f in os.listdir(physio_dir)
        if f.endswith(".hea") and os.path.exists(os.path.join(physio_dir, f[:-4] + ".dat"))
    }, key=lambda r: (len(r), r))

    return [
        {
            "id": rid,
            "description": CURATED_DESCRIPTIONS.get(rid, f"Bản ghi MIT-BIH #{rid}"),
            "is_default": rid == DEFAULT_RECORD,
        }
        for rid in record_ids
    ]


def record_exists(record_id: str) -> bool:
    if not record_id or any(c in record_id for c in ("/", "\\", "..")):
        return False
    physio_dir = _abs_physio_dir()
    return os.path.exists(os.path.join(physio_dir, f"{record_id}.hea")) and \
        os.path.exists(os.path.join(physio_dir, f"{record_id}.dat"))


@router.get("/api/records")
async def get_records():
    """CP3.4: Danh sách bản ghi PhysioNet MIT-BIH khả dụng để chọn stream, kèm mô tả lâm sàng
    ngắn cho các bản ghi tiêu biểu. Dùng id trả về làm query param khi mở WebSocket:
    ws://localhost:8000/ws/ecg?record=<id>
    """
    records = list_available_records()
    return {
        "default_record": DEFAULT_RECORD,
        "count": len(records),
        "records": records,
    }
