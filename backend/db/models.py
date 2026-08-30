import enum
from datetime import datetime

from sqlalchemy import ForeignKey, JSON, String, Text, BigInteger, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.db.base import Base


class UserRole(str, enum.Enum):
    """3 vai trò của hệ thống — xem plan.md mục 5.2/5.3 (Admin/Doctor/Nurse)."""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"


class ReviewStatus(str, enum.Enum):
    """Trạng thái xác nhận của bác sĩ với 1 sự kiện bất thường AI phát hiện (CP5.4 - Human-in-the-loop)."""
    PENDING = "pending"
    APPROVED = "approved"
    CORRECTED = "corrected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False, default=UserRole.NURSE)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    reviewed_anomalies: Mapped[list["AnomalyEvent"]] = relationship(back_populates="reviewer")
    audit_trails: Mapped[list["AuditTrail"]] = relationship(back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    bed_number: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    admission_date: Mapped[datetime | None] = mapped_column(nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)  # tiền sử bệnh, free text
    attending_doctor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Bản ghi PhysioNet đang gán để stream cho bệnh nhân này (id từ GET /api/records, vd "208")
    active_record_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    ecg_records: Mapped[list["EcgRecord"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    anomaly_events: Mapped[list["AnomalyEvent"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class EcgRecord(Base):
    """1 phiên theo dõi/stream ECG của 1 bệnh nhân (không phải bản ghi PhysioNet gốc — đó là `physionet_record_id`)."""
    __tablename__ = "ecg_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    physionet_record_id: Mapped[str] = mapped_column(String(16), nullable=False)  # vd "208"
    started_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="ecg_records")
    anomaly_events: Mapped[list["AnomalyEvent"]] = relationship(back_populates="record", cascade="all, delete-orphan")


class AnomalyEvent(Base):
    """1 nhịp tim bất thường AI phát hiện được — nguồn dữ liệu cho CP5.3 (query lịch sử)
    và CP5.4 (bác sĩ xác nhận/sửa nhãn)."""
    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True, nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey("ecg_records.id"), index=True, nullable=False)
    prediction_label: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    heatmap: Mapped[list | None] = mapped_column(JSON, nullable=True)  # mảng 187 float Grad-CAM
    r_peak_sample: Mapped[int | None] = mapped_column(nullable=True)
    timestamp_ms: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)

    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_status: Mapped[ReviewStatus] = mapped_column(
        SAEnum(ReviewStatus), nullable=False, default=ReviewStatus.PENDING
    )
    corrected_label: Mapped[str | None] = mapped_column(String(64), nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="anomaly_events")
    record: Mapped["EcgRecord"] = relationship(back_populates="anomaly_events")
    reviewer: Mapped["User | None"] = relationship(back_populates="reviewed_anomalies")


class AuditTrail(Base):
    """Nhật ký kiểm toán — ai làm gì lúc nào (CP5.4 ghi log mỗi lần bác sĩ verify, có thể mở
    rộng dùng cho các hành động khác trong tương lai như tắt chuông, sửa hồ sơ bệnh nhân)."""
    __tablename__ = "audit_trails"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # vd "anomaly.verify", "alarm.mute"
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)  # vd "anomaly_event"
    target_id: Mapped[int] = mapped_column(nullable=False)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now(), index=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="audit_trails")
