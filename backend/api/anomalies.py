from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import AnomalyEvent, User
from backend.db.session import get_db

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


class AnomalyEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    record_id: int
    prediction_label: str
    confidence: Optional[float]
    r_peak_sample: Optional[int]
    timestamp_ms: int
    review_status: str
    corrected_label: Optional[str]
    # Không trả `heatmap` (mảng 187 float) trong danh sách để tránh payload phình to khi
    # phân trang nhiều mục — muốn xem XAI chi tiết 1 sự kiện thì dùng luồng real-time hiện có.


class AnomalyListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[AnomalyEventOut]


def _to_utc_ms(dt: datetime) -> int:
    """Quy đổi datetime sang epoch mili-giây. Nếu client gửi datetime KHÔNG có timezone
    (vd '2026-08-30T00:00:00'), coi như UTC (tránh phụ thuộc timezone hệ thống của server)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


@router.get("", response_model=AnomalyListResponse)
def list_anomalies(
    patient_id: Optional[int] = None,
    date_from: Optional[datetime] = Query(default=None, alias="from", description="ISO 8601, vd 2026-08-30T00:00:00Z"),
    date_to: Optional[datetime] = Query(default=None, alias="to", description="ISO 8601"),
    label: Optional[str] = Query(default=None, description="Lọc đúng 1 nhãn AAMI, vd 'CẢNH BÁO: NHỊP THẤT (V)'"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    current_user: User = Depends(get_current_user),  # mọi role đã đăng nhập đều xem được (chỉ cần hợp lệ)
    db: Session = Depends(get_db),
):
    """CP5.3: Lịch sử sự kiện bất thường AI đã phát hiện, có lọc + phân trang.
    Sắp xếp mới nhất trước (`timestamp_ms` giảm dần)."""
    query = db.query(AnomalyEvent)

    if patient_id is not None:
        query = query.filter(AnomalyEvent.patient_id == patient_id)
    if date_from is not None:
        query = query.filter(AnomalyEvent.timestamp_ms >= _to_utc_ms(date_from))
    if date_to is not None:
        query = query.filter(AnomalyEvent.timestamp_ms <= _to_utc_ms(date_to))
    if label is not None:
        query = query.filter(AnomalyEvent.prediction_label == label)

    total = query.count()
    items = (
        query.order_by(AnomalyEvent.timestamp_ms.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AnomalyListResponse(total=total, page=page, page_size=page_size, items=items)
