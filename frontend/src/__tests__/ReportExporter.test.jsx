import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ReportExporter from '../pages/ReportExporter';
import { PatientProvider } from '../context/PatientContext';

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
    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:fake');
  });

  afterEach(() => {
    window.localStorage.removeItem('ecg_patients');
    vi.resetAllMocks();
  });

  it('renders buttons and triggers CSV creation', async () => {
    render(
      <PatientProvider>
        <ReportExporter />
      </PatientProvider>
    );

    const csvBtn = await screen.findByRole('button', { name: /Xuất CSV/i });
    expect(csvBtn).toBeInTheDocument();

    fireEvent.click(csvBtn);
    expect(global.URL.createObjectURL).toHaveBeenCalled();
  });
});
