from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.models import Patient, User
from backend.db.session import get_db

router = APIRouter(prefix="/api/patients", tags=["patients"])

DEFAULT_PATIENT_NAME = "(Chưa gán bệnh nhân)"


class PatientSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    bed_number: Optional[str] = None
    diagnosis: Optional[str] = None
    attending_doctor: Optional[str] = None
    active_record_id: Optional[str] = None


class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    bed_number: Optional[str] = None
    bedNumber: Optional[str] = None
    diagnosis: Optional[str] = None
    attending_doctor: Optional[str] = None
    attendingDoctor: Optional[str] = None
    active_record_id: Optional[str] = None
    activeRecordId: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    bed_number: Optional[str] = None
    bedNumber: Optional[str] = None
    diagnosis: Optional[str] = None
    attending_doctor: Optional[str] = None
    attendingDoctor: Optional[str] = None
    active_record_id: Optional[str] = None
    activeRecordId: Optional[str] = None


def _serialize_patient(p: Patient) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "gender": p.gender,
        "bed_number": p.bed_number,
        "bedNumber": p.bed_number,
        "diagnosis": p.diagnosis,
        "attending_doctor": p.attending_doctor,
        "attendingDoctor": p.attending_doctor,
        "active_record_id": p.active_record_id,
        "activeRecordId": p.active_record_id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get("")
def list_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Danh sách bệnh nhân đang quản lý (bỏ qua bản ghi tạm '(Chưa gán bệnh nhân)')."""
    patients = (
        db.query(Patient)
        .filter(Patient.name != DEFAULT_PATIENT_NAME)
        .order_by(Patient.id.desc())
        .all()
    )
    return {"patients": [_serialize_patient(p) for p in patients]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bed = payload.bed_number or payload.bedNumber
    doctor = payload.attending_doctor or payload.attendingDoctor
    record_id = payload.active_record_id or payload.activeRecordId

    patient = Patient(
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        bed_number=bed,
        diagnosis=payload.diagnosis,
        attending_doctor=doctor,
        active_record_id=record_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {"patient": _serialize_patient(patient)}


@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    payload: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bệnh nhân")

    if payload.name is not None:
        patient.name = payload.name
    if payload.age is not None:
        patient.age = payload.age
    if payload.gender is not None:
        patient.gender = payload.gender
    bed = payload.bed_number or payload.bedNumber
    if bed is not None:
        patient.bed_number = bed
    if payload.diagnosis is not None:
        patient.diagnosis = payload.diagnosis
    doctor = payload.attending_doctor or payload.attendingDoctor
    if doctor is not None:
        patient.attending_doctor = doctor
    record_id = payload.active_record_id or payload.activeRecordId
    if record_id is not None:
        patient.active_record_id = record_id

    db.commit()
    db.refresh(patient)
    return {"patient": _serialize_patient(patient)}


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bệnh nhân")

    db.delete(patient)
    db.commit()
    return {"status": "success", "message": "Đã xoá bệnh nhân"}
