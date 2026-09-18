import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../api/axios';

const PatientContext = createContext();

export const usePatient = () => useContext(PatientContext);

const STORAGE_KEY = 'ecg_patients';

const normalize = (p) => {
  if (!p) return p;
  return {
    id: p.id,
    name: p.name || p.fullName || '',
    age: p.age || '',
    gender: p.gender || p.sex || '',
    bedNumber: p.bedNumber || p.bed_number || p.bed || '',
    activeRecordId: p.activeRecordId || p.active_record_id || p.active_record || p.activeRecord || null,
    attendingDoctor: p.attendingDoctor || p.attending_doctor || p.attending || '',
    diagnosis: p.diagnosis || '',
    ...p,
  };
};

export const PatientProvider = ({ children }) => {
  const [patients, setPatients] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const arr = raw ? JSON.parse(raw) : [];
      return arr.map(normalize);
    } catch (e) {
      console.error('Failed parse patients from localStorage', e);
      return [];
    }
  });

  const [serverAvailable, setServerAvailable] = useState(false);

  // Probe backend to see if /api/patients exists and optionally merge server list
  useEffect(() => {
    let cancelled = false;
    const probe = async () => {
      try {
        const res = await api.get('/api/patients', { timeout: 2000 });
        if (cancelled) return;
        setServerAvailable(true);
        // Merge server patients (server wins remoteId & stable data)
        if (Array.isArray(res.data?.patients)) {
          setPatients(prev => {
            const byRemote = new Map(prev.filter(p => p.remoteId).map(p => [p.remoteId, p]));
            const merged = res.data.patients.map(sp => {
              const local = byRemote.get(sp.id);
              return normalize({ ...local, ...sp, remoteId: sp.id });
            });
            // keep local-only patients too
            const localOnly = prev.filter(p => !p.remoteId);
            return [...merged, ...localOnly];
          });
        }
      } catch (e) {
        setServerAvailable(false);
      }
    };
    probe();
    return () => { cancelled = true; };
  }, []);

  const [selectedPatient, setSelectedPatient] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY + '_selected');
      return raw ? normalize(JSON.parse(raw)) : null;
    } catch (e) {
      return null;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(patients));
    } catch (e) {
      console.error('Failed write patients to localStorage', e);
    }
  }, [patients]);

  useEffect(() => {
    try {
      if (selectedPatient) {
        localStorage.setItem(STORAGE_KEY + '_selected', JSON.stringify(selectedPatient));
      } else {
        localStorage.removeItem(STORAGE_KEY + '_selected');
      }
    } catch (e) {
      console.error('Failed write selected patient', e);
    }
  }, [selectedPatient]);

  const addPatient = (p) => {
    const payload = normalize({ id: Date.now(), ...p });
    setPatients(prev => [payload, ...prev]);
    setSelectedPatient(payload);

    // Try to sync to server asynchronously
    (async () => {
      if (!serverAvailable) return;
      try {
        const res = await api.post('/api/patients', payload);
        const server = res.data?.patient || res.data;
        if (server && server.id) {
          // update patient with remoteId
          setPatients(prev => prev.map(x => x.id === payload.id ? { ...x, remoteId: server.id, ...normalize(server) } : x));
          setSelectedPatient(prev => prev?.id === payload.id ? { ...prev, remoteId: server.id, ...normalize(server) } : prev);
        }
      } catch (e) {
        // ignore; fallback to local-only
      }
    })();
  };

  const updatePatient = (id, patch) => {
    const patched = normalize({ ...patch, id });
    setPatients(prev => prev.map(x => x.id === id ? { ...x, ...patched } : x));
    if (selectedPatient && selectedPatient.id === id) {
      setSelectedPatient(prev => ({ ...prev, ...patched }));
    }

    (async () => {
      // best-effort sync to server
      try {
        const target = (patched.remoteId) ? `/api/patients/${patched.remoteId}` : (serverAvailable ? `/api/patients/${id}` : null);
        if (!target) return;
        await api.put(target, patched);
      } catch (e) {
        // ignore
      }
    })();
  };

  // Sinh nhanh 1 bệnh nhân demo / 1 bản ghi MIT-BIH đang có sẵn (dùng khi mới cài đặt hệ
  // thống, chưa có dữ liệu bệnh nhân thật) - tránh phải tạo tay từng người qua form cho mỗi
  // bản ghi muốn thử. Bỏ qua bản ghi đã có sẵn 1 bệnh nhân dùng nó (tránh tạo trùng nếu bấm
  // nút nhiều lần). Trả về số bệnh nhân mới đã tạo.
  const seedDemoPatients = async () => {
    const res = await api.get('/api/records');
    const records = res.data?.records || [];
    const usedRecordIds = new Set(patients.map(p => String(p.activeRecordId)));
    const toSeed = records.filter(r => !usedRecordIds.has(String(r.id)));
    if (toSeed.length === 0) return 0;

    const startIndex = patients.length;
    const genders = ['M', 'F'];
    const today = new Date().toISOString().split('T')[0];
    const newPatients = toSeed.map((r, i) => normalize({
      id: Date.now() + i,
      name: `Bệnh nhân mẫu #${r.id}`,
      age: 30 + (parseInt(r.id, 10) % 50),
      gender: genders[i % 2],
      bedNumber: `G${String(startIndex + i + 1).padStart(2, '0')}`,
      admissionDate: today,
      diagnosis: r.description || '',
      attendingDoctor: '',
      activeRecordId: r.id,
    }));

    setPatients(prev => [...newPatients, ...prev]);
    return newPatients.length;
  };

  const removePatient = (id) => {
    setPatients(prev => prev.filter(x => x.id !== id));
    if (selectedPatient && selectedPatient.id === id) setSelectedPatient(null);

    (async () => {
      try {
        // try server delete if remoteId exists
        const local = patients.find(p => p.id === id);
        const rid = local?.remoteId;
        if (rid) await api.delete(`/api/patients/${rid}`);
      } catch (e) {
        // ignore
      }
    })();
  };

  const value = {
    patients,
    addPatient,
    updatePatient,
    removePatient,
    seedDemoPatients,
    selectedPatient,
    setSelectedPatient,
    // Backwards compatibility aliases
    activePatient: selectedPatient,
    selectPatient: setSelectedPatient,
    clearActivePatient: () => setSelectedPatient(null),
    deletePatient: removePatient,
  };

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  );
};

export default PatientContext;
