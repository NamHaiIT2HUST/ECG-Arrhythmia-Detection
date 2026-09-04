import React, { useState, useEffect } from 'react';
import api from '../../api/axios';

const RecordSelector = ({ selectedRecord, onSelectRecord }) => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await api.get('/api/records');
        if (response.data && response.data.records) {
          setRecords(response.data.records);
          if (!selectedRecord && response.data.default_record) onSelectRecord(response.data.default_record);
        }
      } catch (error) {
        console.error('Lỗi lấy danh sách bản ghi:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, [selectedRecord, onSelectRecord]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      <label style={{ color: 'var(--text-muted)', fontWeight: '500', fontSize: '14px' }}>
        Bản ghi MIT-BIH:
      </label>
      <select 
        value={selectedRecord || ''} 
        onChange={(e) => onSelectRecord(e.target.value)}
        style={{
          padding: '8px 12px',
          borderRadius: '6px',
          border: '1px solid #334155',
          backgroundColor: 'var(--card-bg)',
          color: 'var(--text-main)',
          fontSize: '14px',
          outline: 'none',
          cursor: 'pointer',
          minWidth: '200px'
        }}
        disabled={loading}
      >
        {loading ? (
          <option>Đang tải...</option>
        ) : (
          records.map(record => (
            <option key={record.id} value={record.id}>
              {record.id} - {record.description}
            </option>
          ))
        )}
      </select>
    </div>
  );
};

export default RecordSelector;
