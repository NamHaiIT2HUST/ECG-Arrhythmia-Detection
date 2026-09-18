import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ReportExporter from '../pages/ReportExporter';
import { PatientProvider } from '../context/PatientContext';
import { AnomalyProvider } from '../context/AnomalyContext';

// vi.mock được hoist lên đầu file bởi Vitest - phải đặt ở top-level (không phải trong
// beforeEach) để có tác dụng TRƯỚC khi PatientContext import '../api/axios' phía trên.
// axios.js dùng `export default api`, nên factory phải trả về key `default` mới đúng chỗ.
vi.mock('../api/axios', () => ({ default: { get: vi.fn().mockRejectedValue(new Error('no server')) } }));

describe('ReportExporter', () => {
  beforeEach(() => {
    // Set localStorage patients
    window.localStorage.setItem('ecg_patients', JSON.stringify([
      { id: 1, name: 'Nguyen Van A', bedNumber: 'B12', activeRecordId: '208' }
    ]));
    // Mock URL.createObjectURL/revokeObjectURL - jsdom không có sẵn, generateCSV gọi cả 2
    global.URL.createObjectURL = vi.fn(() => 'blob:fake');
    global.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    window.localStorage.removeItem('ecg_patients');
    vi.resetAllMocks();
  });

  it('renders buttons and triggers CSV creation after choosing a patient', async () => {
    render(
      <PatientProvider>
        <AnomalyProvider>
          <ReportExporter />
        </AnomalyProvider>
      </PatientProvider>
    );

    // Trang mới bắt buộc chọn 1 bệnh nhân trước khi bật nút xuất - chưa chọn ai thì
    // "Xuất CSV" ở trạng thái disabled (xem ReportExporter.jsx).
    const select = await screen.findByRole('combobox');
    fireEvent.change(select, { target: { value: '1' } });

    const csvBtn = await screen.findByRole('button', { name: /Xuất CSV/i });
    expect(csvBtn).toBeInTheDocument();
    expect(csvBtn).not.toBeDisabled();

    fireEvent.click(csvBtn);
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });
});
