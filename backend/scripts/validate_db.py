"""
Kiem chung nhanh CP5.1: dung 1 SQLite in-memory rieng (khong dung file dev thuc), tao het
5 bang tu Base.metadata, insert + query qua ORM cho tung bang va tung quan he (relationship)
de chac chan model.py mo ta dung schema da thiet ke trong plan.md muc 5.2.

Chay: python -m backend.scripts.validate_db
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.base import Base
from backend.db.models import User, UserRole, Patient, EcgRecord, AnomalyEvent, ReviewStatus, AuditTrail


def run():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # 1. Insert theo dung thu tu phu thuoc khoa ngoai
    doctor = User(username="bs_hai", hashed_password="fake_hash_khong_dung_that", role=UserRole.DOCTOR)
    db.add(doctor)
    db.flush()
    assert doctor.id is not None, "User chua duoc gan id sau flush"

    patient = Patient(name="Nguyen Van A", age=65, gender="M", bed_number="A101",
                       diagnosis="Tien su PVC", attending_doctor="BS. Hai", active_record_id="208")
    db.add(patient)
    db.flush()
    assert patient.id is not None

    record = EcgRecord(patient_id=patient.id, physionet_record_id="208")
    db.add(record)
    db.flush()
    assert record.id is not None

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    anomaly = AnomalyEvent(
        patient_id=patient.id, record_id=record.id,
        prediction_label="CẢNH BÁO: NHỊP THẤT (V)", confidence=0.97,
        heatmap=[0.1, 0.5, 0.9], r_peak_sample=209, timestamp_ms=now_ms,
    )
    db.add(anomaly)
    db.flush()
    assert anomaly.id is not None
    assert anomaly.review_status == ReviewStatus.PENDING, "Mac dinh review_status phai la PENDING"

    # 2. Bac si xac nhan (CP5.4 se lam qua API, o day chi test truc tiep qua ORM)
    anomaly.reviewed_by = doctor.id
    anomaly.review_status = ReviewStatus.APPROVED
    db.flush()

    audit = AuditTrail(user_id=doctor.id, action="anomaly.verify", target_type="anomaly_event",
                        target_id=anomaly.id, detail={"status": "approved"})
    db.add(audit)
    db.commit()

    # 3. Query lai + kiem tra quan he 2 chieu (relationship)
    fetched_patient = db.query(Patient).filter_by(bed_number="A101").one()
    assert len(fetched_patient.ecg_records) == 1, "Patient.ecg_records phai co dung 1 phien"
    assert len(fetched_patient.anomaly_events) == 1, "Patient.anomaly_events phai co dung 1 su kien"

    fetched_anomaly = fetched_patient.anomaly_events[0]
    assert fetched_anomaly.record.physionet_record_id == "208", "AnomalyEvent.record phai tro dung EcgRecord"
    assert fetched_anomaly.reviewer.username == "bs_hai", "AnomalyEvent.reviewer phai tro dung User"
    assert fetched_anomaly.heatmap == [0.1, 0.5, 0.9], "Cot JSON heatmap phai doc/ghi dung"

    fetched_doctor = db.query(User).filter_by(username="bs_hai").one()
    assert len(fetched_doctor.reviewed_anomalies) == 1, "User.reviewed_anomalies phai co dung 1 muc"
    assert len(fetched_doctor.audit_trails) == 1, "User.audit_trails phai co dung 1 muc"

    db.close()
    print("[✓] Tất cả 5 bảng (users, patients, ecg_records, anomaly_events, audit_trails)")
    print("[✓] Insert/query/relationship 2 chiều đều đúng — CP 5.1 sẵn sàng.")


if __name__ == "__main__":
    run()
