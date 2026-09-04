import React, { useState } from 'react';
import { usePatient } from '../../context/PatientContext';

const PatientList = () => {
  const { patients, addPatient, updatePatient, removePatient, selectedPatient, setSelectedPatient } = usePatient();
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', age: '', gender: '', bedNumber: '', activeRecordId: '' });

  const startAdd = () => { setEditing('add'); setForm({ name: '', age: '', gender: '', bedNumber: '', activeRecordId: '' }); };
  const startEdit = (p) => { setEditing(p.id); setForm({ name: p.name||'', age: p.age||'', gender: p.gender||'', bedNumber: p.bedNumber||'', activeRecordId: p.activeRecordId||'' }); };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editing === 'add') {
      addPatient(form);
    } else {
      updatePatient(editing, form);
    }
    setEditing(null);
  };

  return (
    <div style={{ width: '420px', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>Quản lý bệnh nhân</h3>
        <button onClick={startAdd} style={{ padding: '6px 10px' }}>+ Thêm</button>
      </div>

      {editing && (
        <form onSubmit={handleSubmit} style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <input placeholder="Họ tên" value={form.name} onChange={e=>setForm({...form, name: e.target.value})} />
          <input placeholder="Tuổi" value={form.age} onChange={e=>setForm({...form, age: e.target.value})} />
          <input placeholder="Giới tính" value={form.gender} onChange={e=>setForm({...form, gender: e.target.value})} />
          <input placeholder="Phòng / Giường" value={form.bedNumber} onChange={e=>setForm({...form, bedNumber: e.target.value})} />
          <input placeholder="Active record id (vd 208)" value={form.activeRecordId} onChange={e=>setForm({...form, activeRecordId: e.target.value})} />
          <div style={{ display: 'flex', gap: 8 }}>
            <button type="submit">Lưu</button>
            <button type="button" onClick={()=>{ setEditing(null); }}>Hủy</button>
          </div>
        </form>
      )}

      <div style={{ marginTop: 12 }}>
        {patients.length === 0 ? (
          <p style={{ color: '#64748b' }}>Chưa có bệnh nhân.</p>
        ) : (
          patients.map(p => (
            <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px', border: '1px solid #e2e8f0', borderRadius: 6, marginBottom: 8, background: selectedPatient?.id===p.id ? '#eef2ff' : '#fff' }}>
                <div style={{ cursor: 'pointer' }} onClick={() => setSelectedPatient(p)}>
                <div style={{ fontWeight: 700 }}>{p.name}</div>
                <div style={{ fontSize: 12, color: '#64748b' }}>{p.bedNumber} • {p.age} • {p.gender}</div>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                <button onClick={() => startEdit(p)}>Sửa</button>
                <button onClick={() => removePatient(p.id)} style={{ color: '#b91c1c' }}>Xóa</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default PatientList;
