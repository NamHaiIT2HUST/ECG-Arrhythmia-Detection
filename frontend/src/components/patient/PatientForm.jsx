import React, { useState } from 'react';
import { usePatient } from '../../context/PatientContext';

const GENDER_OPTIONS = [
  { value: 'M', label: 'Nam' },
  { value: 'F', label: 'Nữ' },
  { value: 'Other', label: 'Khác' },
];

const inputStyle = {
  width: '100%',
  padding: '9px 12px',
  borderRadius: '6px',
  border: '1px solid #334155',
  backgroundColor: '#1e293b',
  color: '#f8fafc',
  fontSize: '14px',
  outline: 'none',
  boxSizing: 'border-box',
};

const labelStyle = {
  display: 'block',
  fontSize: '12px',
  color: '#94a3b8',
  fontWeight: '600',
  marginBottom: '5px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const PatientForm = ({ patient, onClose, records = [] }) => {
  const { addPatient, updatePatient, patients } = usePatient();
  const isEdit = !!patient;

  const [form, setForm] = useState({
    name: patient?.name || '',
    age: patient?.age ?? '',
    gender: patient?.gender || 'M',
    bedNumber: patient?.bedNumber || '',
    admissionDate: patient?.admissionDate || new Date().toISOString().split('T')[0],
    diagnosis: patient?.diagnosis || '',
    attendingDoctor: patient?.attendingDoctor || '',
    vitals: {
      bloodPressure: patient?.vitals?.bloodPressure || '120/80',
      spo2: patient?.vitals?.spo2 ?? 98,
    },
    activeRecordId: patient?.activeRecordId || '208',
  });

  const [errors, setErrors] = useState({});

  const set = (field, value) => setForm(prev => ({ ...prev, [field]: value }));
  const setVital = (field, value) => setForm(prev => ({
    ...prev, vitals: { ...prev.vitals, [field]: value }
  }));

  const validate = () => {
    const errs = {};
    if (!form.name.trim()) errs.name = 'Tên bắt buộc';
    const age = Number(form.age);
    if (isNaN(age) || age < 0 || age > 120) errs.age = 'Tuổi phải từ 0-120';
    if (!form.bedNumber.trim()) errs.bedNumber = 'Số giường bắt buộc';
    else {
      const dup = patients.find(
        p => p.bedNumber === form.bedNumber && p.id !== patient?.id
      );
      if (dup) errs.bedNumber = `Giường ${form.bedNumber} đã có bệnh nhân: ${dup.name}`;
    }
    return errs;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    const data = { ...form, age: Number(form.age) };
    if (isEdit) {
      updatePatient(patient.id, data);
    } else {
      addPatient(data);
    }
    onClose();
  };

  const Field = ({ label, error, children }) => (
    <div>
      <label style={labelStyle}>{label}</label>
      {children}
      {error && <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#f87171' }}>{error}</p>}
    </div>
  );

  return (
    <div style={{
      position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.6)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
    }}>
      <div style={{
        width: '560px', maxWidth: '95%', maxHeight: '90vh', overflowY: 'auto',
        backgroundColor: '#0f172a', borderRadius: '12px', padding: '28px',
        border: '1px solid #1e293b', boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ margin: 0, color: '#f8fafc', fontSize: '18px' }}>
            {isEdit ? '✏️ Sửa hồ sơ bệnh nhân' : '➕ Thêm bệnh nhân mới'}
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: '22px', cursor: 'pointer', lineHeight: 1 }}>✕</button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Row 1 */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Field label="Họ và tên *" error={errors.name}>
              <input style={inputStyle} value={form.name} onChange={e => set('name', e.target.value)} placeholder="Nguyễn Văn A" />
            </Field>
            <Field label="Số giường *" error={errors.bedNumber}>
              <input style={inputStyle} value={form.bedNumber} onChange={e => set('bedNumber', e.target.value)} placeholder="G01" />
            </Field>
          </div>

          {/* Row 2 */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
            <Field label="Tuổi" error={errors.age}>
              <input style={inputStyle} type="number" min="0" max="120" value={form.age} onChange={e => set('age', e.target.value)} placeholder="45" />
            </Field>
            <Field label="Giới tính">
              <select style={inputStyle} value={form.gender} onChange={e => set('gender', e.target.value)}>
                {GENDER_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </Field>
            <Field label="Ngày nhập viện">
              <input style={inputStyle} type="date" value={form.admissionDate} onChange={e => set('admissionDate', e.target.value)} />
            </Field>
          </div>

          {/* Row 3 */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Field label="Bác sĩ phụ trách">
              <input style={inputStyle} value={form.attendingDoctor} onChange={e => set('attendingDoctor', e.target.value)} placeholder="BS. Trần Minh Tuấn" />
            </Field>
            <Field label="Bản ghi ECG đang stream">
              <select style={inputStyle} value={form.activeRecordId} onChange={e => set('activeRecordId', e.target.value)}>
                {records.length > 0 ? records.map(r => (
                  <option key={r.id} value={r.id}>{r.id} — {r.description}</option>
                )) : (
                  <option value="208">208 — Mặc định (PVC)</option>
                )}
              </select>
            </Field>
          </div>

          {/* Row 4 */}
          <Field label="Tiền sử bệnh / Chẩn đoán">
            <textarea
              style={{ ...inputStyle, minHeight: '70px', resize: 'vertical' }}
              value={form.diagnosis}
              onChange={e => set('diagnosis', e.target.value)}
              placeholder="Rối loạn nhịp tim, tăng huyết áp..."
            />
          </Field>

          {/* Row 5 — Vitals */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <Field label="Huyết áp (mmHg)">
              <input style={inputStyle} value={form.vitals.bloodPressure} onChange={e => setVital('bloodPressure', e.target.value)} placeholder="120/80" />
            </Field>
            <Field label="SpO2 (%)">
              <input style={inputStyle} type="number" min="0" max="100" value={form.vitals.spo2} onChange={e => setVital('spo2', Number(e.target.value))} placeholder="98" />
            </Field>
          </div>

          {/* Buttons */}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '8px' }}>
            <button type="button" onClick={onClose} style={{
              padding: '10px 20px', background: 'transparent', color: '#94a3b8',
              border: '1px solid #334155', borderRadius: '6px', cursor: 'pointer', fontWeight: '600'
            }}>
              Hủy
            </button>
            <button type="submit" style={{
              padding: '10px 24px', background: 'var(--primary)', color: 'white',
              border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '600'
            }}>
              {isEdit ? 'Lưu thay đổi' : 'Thêm bệnh nhân'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientForm;
