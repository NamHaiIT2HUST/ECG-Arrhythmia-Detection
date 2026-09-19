import React, { useState, useEffect } from 'react';
import { usePatient } from '../context/PatientContext';
import PatientCard from '../components/patient/PatientCard';
import PatientForm from '../components/patient/PatientForm';
import api from '../api/axios';

const PatientPage = () => {
  const { patients, activePatient, selectPatient, clearActivePatient, deletePatient, seedDemoPatients } = usePatient();
  const [showForm, setShowForm] = useState(false);
  const [editingPatient, setEditingPatient] = useState(null);
  const [records, setRecords] = useState([]);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedError, setSeedError] = useState(null);
  const [query, setQuery] = useState('');

  const normalizedQuery = query.trim().toLowerCase();
  const filteredPatients = normalizedQuery
    ? patients.filter((p) => [p.name, p.bedNumber, p.attendingDoctor]
        .some((field) => String(field || '').toLowerCase().includes(normalizedQuery)))
    : patients;

  const handleSeedDemoPatients = async () => {
    setIsSeeding(true);
    setSeedError(null);
    try {
      const count = await seedDemoPatients();
      if (count === 0) setSeedError('Tất cả bản ghi mẫu đã có bệnh nhân tương ứng.');
    } catch {
      setSeedError('Không tạo được bệnh nhân mẫu. Kiểm tra kết nối backend.');
    } finally {
      setIsSeeding(false);
    }
  };

  // Tải danh sách bản ghi MIT-BIH để dùng trong PatientForm
  useEffect(() => {
    api.get('/api/records')
      .then(res => setRecords(res.data?.records || []))
      .catch(() => {});
  }, []);

  const handleSelect = (patient) => {
    if (activePatient?.id === patient.id) {
      clearActivePatient();
    } else {
      selectPatient(patient);
    }
  };

  const handleEdit = (patient) => {
    setEditingPatient(patient);
    setShowForm(true);
  };

  const handleDelete = (id) => {
    if (window.confirm('Bạn có chắc muốn xóa hồ sơ bệnh nhân này không?')) {
      deletePatient(id);
    }
  };

  const handleAddNew = () => {
    setEditingPatient(null);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingPatient(null);
  };

  return (
    <div style={{ padding: '25px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: '0 0 4px', color: 'var(--text-main)', fontSize: '22px', fontWeight: '700' }}>
            🗂️ Quản Lý Hồ Sơ Bệnh Nhân
          </h2>
          <p style={{ margin: 0, fontSize: '14px', color: 'var(--text-muted)' }}>
            {patients.length} bệnh nhân đang quản lý
            {activePatient && ` · Đang theo dõi: ${activePatient.name} (Giường ${activePatient.bedNumber})`}
          </p>
        </div>
        <button
          onClick={handleAddNew}
          id="add-patient-btn"
          style={{
            padding: '10px 20px',
            backgroundColor: 'var(--primary)',
            color: 'white',
            border: 'none',
            borderRadius: '7px',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          ＋ Thêm bệnh nhân
        </button>
      </div>

      {/* Hướng dẫn */}
      {patients.length === 0 ? (
        <div className="card" style={{ padding: '60px 40px', textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏥</div>
          <h3 style={{ color: 'var(--text-main)', marginBottom: '8px' }}>Chưa có bệnh nhân nào</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '14px' }}>
            Bấm "Thêm bệnh nhân" để tạo hồ sơ đầu tiên. Sau khi thêm, bấm vào card để bắt đầu theo dõi bệnh nhân đó trên Dashboard.
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={handleAddNew} style={{
              padding: '10px 24px', backgroundColor: 'var(--primary)', color: 'white',
              border: 'none', borderRadius: '7px', fontWeight: '600', cursor: 'pointer'
            }}>
              ＋ Thêm bệnh nhân đầu tiên
            </button>
            <button
              onClick={handleSeedDemoPatients}
              disabled={isSeeding}
              style={{
                padding: '10px 24px', backgroundColor: 'transparent', color: 'var(--primary)',
                border: '1px solid var(--primary)', borderRadius: '7px', fontWeight: '600',
                cursor: isSeeding ? 'default' : 'pointer', opacity: isSeeding ? 0.7 : 1,
              }}
            >
              {isSeeding ? 'Đang tạo...' : '＋ Tạo bệnh nhân mẫu từ bản ghi có sẵn'}
            </button>
          </div>
          {seedError && (
            <p style={{ marginTop: '12px', color: 'var(--danger)', fontSize: '12.5px' }}>{seedError}</p>
          )}
        </div>
      ) : (
        <>
          {/* Tìm kiếm nhanh theo tên/số giường/bác sĩ phụ trách */}
          <div style={{ position: 'relative', maxWidth: '360px' }}>
            <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '14px', pointerEvents: 'none' }}>
              🔍
            </span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Tìm theo tên, số giường hoặc bác sĩ phụ trách..."
              style={{
                width: '100%', padding: '10px 14px 10px 34px', borderRadius: '8px',
                border: '1px solid var(--border-color)', background: 'var(--card-bg)',
                color: 'var(--text-main)', fontSize: '13.5px', boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Active patient banner */}
          {activePatient && (
            <div style={{
              backgroundColor: '#eff6ff', border: '1px solid #bfdbfe',
              borderRadius: '8px', padding: '12px 16px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <span style={{ fontSize: '14px', color: '#1d4ed8', fontWeight: '500' }}>
                📡 Dashboard đang stream bản ghi MIT-BIH <strong>#{activePatient.activeRecordId}</strong> cho bệnh nhân <strong>{activePatient.name}</strong> (Giường {activePatient.bedNumber})
              </span>
              <button
                onClick={clearActivePatient}
                style={{ background: 'none', border: '1px solid #93c5fd', borderRadius: '5px', color: '#1d4ed8', padding: '4px 12px', cursor: 'pointer', fontSize: '13px' }}
              >
                Hủy chọn
              </button>
            </div>
          )}

          {/* Grid */}
          {filteredPatients.length === 0 ? (
            <div className="card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '14px' }}>
              Không tìm thấy bệnh nhân/giường phù hợp với "{query}".
            </div>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gridAutoRows: 'max-content',
              gap: '16px',
              overflowY: 'auto',
              flex: 1,
              minHeight: 0,
            }}>
              {filteredPatients.map(patient => (
                <PatientCard
                  key={patient.id}
                  patient={patient}
                  isActive={activePatient?.id === patient.id}
                  onSelect={handleSelect}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  latestPrediction={activePatient?.id === patient.id ? activePatient._latestPrediction : null}
                />
              ))}
            </div>
          )}
        </>
      )}

      {/* Form modal */}
      {showForm && (
        <PatientForm
          patient={editingPatient}
          onClose={handleCloseForm}
          records={records}
        />
      )}
    </div>
  );
};

export default PatientPage;
