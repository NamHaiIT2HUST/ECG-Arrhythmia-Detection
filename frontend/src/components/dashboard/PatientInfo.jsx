import React, { useState } from 'react';

const PatientInfo = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [patient, setPatient] = useState({
    name: 'Nguyễn Văn A',
    patientId: 'BN-2026-89',
    age: '45',
    gender: 'Nam',
    room: 'Phòng ICU - Giường 04'
  });

  const handleChange = (e) => {
    setPatient({ ...patient, [e.target.name]: e.target.value });
  };

  return (
    <div className="card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-main)', fontWeight: 'bold' }}>👤 Hồ Sơ Bệnh Nhân</h3>
        <button 
          onClick={() => setIsEditing(!isEditing)}
          style={{ 
            backgroundColor: isEditing ? 'var(--success)' : 'var(--bg-color)', 
            color: isEditing ? 'white' : 'var(--text-main)', 
            border: '1px solid var(--border-color)', 
            padding: '6px 14px', 
            borderRadius: '6px', 
            cursor: 'pointer', 
            fontWeight: 'bold', 
            transition: '0.2s',
            fontSize: '13px'
          }}
        >
          {isEditing ? '💾 Lưu hồ sơ' : '✏️ Cập nhật'}
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Họ tên:</span>
          {isEditing ? (
            <input 
              name="name" 
              value={patient.name} 
              onChange={handleChange} 
              style={{ padding: '6px 10px', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '14px', color: 'var(--text-main)', textAlign: 'right', outline: 'none', width: '60%' }} 
            />
          ) : (
            <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{patient.name}</span>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Mã Bệnh Án:</span>
          {isEditing ? (
            <input 
              name="patientId" 
              value={patient.patientId} 
              onChange={handleChange} 
              style={{ padding: '6px 10px', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '14px', color: 'var(--text-main)', textAlign: 'right', outline: 'none', width: '60%' }} 
            />
          ) : (
            <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{patient.patientId}</span>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Tuổi / Giới tính:</span>
          {isEditing ? (
            <div style={{ display: 'flex', gap: '5px', justifyContent: 'flex-end', width: '60%' }}>
              <input 
                name="age" 
                value={patient.age} 
                onChange={handleChange} 
                style={{ width: '45px', padding: '6px', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '14px', color: 'var(--text-main)', textAlign: 'center', outline: 'none' }} 
              />
              <input 
                name="gender" 
                value={patient.gender} 
                onChange={handleChange} 
                style={{ width: '70px', padding: '6px', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '14px', color: 'var(--text-main)', textAlign: 'center', outline: 'none' }} 
              />
            </div>
          ) : (
            <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{patient.age} / {patient.gender}</span>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Phòng / Giường:</span>
          {isEditing ? (
            <input 
              name="room" 
              value={patient.room} 
              onChange={handleChange} 
              style={{ padding: '6px 10px', border: '1px solid var(--border-color)', borderRadius: '6px', fontSize: '14px', color: 'var(--text-main)', textAlign: 'right', outline: 'none', width: '60%' }} 
            />
          ) : (
            <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{patient.room}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default PatientInfo;