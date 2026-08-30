"""
Ghi lai lich su phien stream + su kien bat thuong vao Database (CP5.3), goi tu
`backend/api/ws_routes.py` moi khi 1 ket noi WebSocket real-time mo/dong hoac phat hien
1 nhip bat thuong.

Ghi chu quan trong ve `patient_id`: Module Quan ly Ho so Benh nhan (CP4.1) hien van luu
o localStorage phia Frontend, CHUA co API tao Patient that trong Database. De khong bi
chan boi CP4.1, `/ws/ecg` chap nhan `patient_id` TUY CHON qua query param - neu khong
truyen (hoac truyen id khong ton tai), dung 1 "benh nhan mac dinh" (tao san neu chua co)
de cac dong FK van hop le. Khi CP4.1 (hoac buoc di cu localStorage -> DB rieng) hoan
thanh, Frontend chi can truyen dung `patient_id` that qua query param, khong can sua gi
them o day.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.db.models import AnomalyEvent, EcgRecord, Patient

DEFAULT_PATIENT_NAME = "(Chưa gán bệnh nhân)"


def get_or_create_default_patient(db: Session) -> Patient:
    patient = db.query(Patient).filter_by(name=DEFAULT_PATIENT_NAME).one_or_none()
    if patient is None:
        patient = Patient(name=DEFAULT_PATIENT_NAME)
        db.add(patient)
        db.flush()
    return patient


def resolve_patient(db: Session, patient_id: int | None) -> Patient:
    """Tra ve Patient dung id truyen vao neu ton tai, nguoc lai fallback ve benh nhan mac dinh."""
    if patient_id is not None:
        patient = db.get(Patient, patient_id)
        if patient is not None:
            return patient
    return get_or_create_default_patient(db)


def start_ecg_record(db: Session, patient_id: int, physionet_record_id: str) -> EcgRecord:
    """Mo 1 phien theo doi moi khi 1 ket noi WebSocket bat dau stream. Goi `db.commit()` ngay
    de co id dung, tranh mat du lieu neu client ngat ket noi dot ngot truoc khi co commit khac."""
    record = EcgRecord(patient_id=patient_id, physionet_record_id=physionet_record_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def end_ecg_record(db: Session, record: EcgRecord) -> None:
    """Danh dau thoi diem ket thuc phien khi WebSocket ngat ket noi."""
    record.ended_at = datetime.now(timezone.utc)
    db.commit()


def log_anomaly(
    db: Session,
    *,
    patient_id: int,
    record_id: int,
    prediction_label: str,
    confidence: float | None,
    heatmap: list | None,
    r_peak_sample: int | None,
    timestamp_ms: int,
) -> AnomalyEvent:
    event = AnomalyEvent(
        patient_id=patient_id,
        record_id=record_id,
        prediction_label=prediction_label,
        confidence=confidence,
        heatmap=heatmap,
        r_peak_sample=r_peak_sample,
        timestamp_ms=timestamp_ms,
    )
    db.add(event)
    db.commit()
    return event
