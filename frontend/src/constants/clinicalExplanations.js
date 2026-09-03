/**
 * clinicalExplanations.js — Bảng tra cứu giải thích lâm sàng theo nhãn AAMI
 * (bản rút gọn có chủ đích — xem plan.md mục 4.5 về giới hạn phạm vi CP4.4)
 * KHÔNG đo PR/QRS/ST thật — chỉ giải thích văn bản theo nhãn đã phân loại.
 */

export const CLINICAL_EXPLANATIONS = {
  'BÌNH THƯỜNG': {
    title: 'Nhịp xoang bình thường (Normal Beat — N)',
    aami_code: 'N',
    mitbih_symbols: 'N, L, R, e, j',
    description: 'Nhịp tim phát sinh từ nút xoang (SA node), lan truyền bình thường qua hệ thống dẫn truyền tim. Điện tâm đồ thường có sóng P rõ ràng, khoảng PR trong giới hạn bình thường (~120-200ms), phức bộ QRS hẹp (<120ms).',
    ai_focus: 'Mô hình tập trung vào hình thái phức bộ QRS cân đối và hẹp, cùng sự xuất hiện đều đặn của sóng P trước mỗi phức bộ.',
    color: '#10b981',
    risk: 'Không có nguy cơ',
    action: 'Tiếp tục theo dõi định kỳ.',
  },
  'CẢNH BÁO: TRÊN THẤT (S)': {
    title: 'Ngoại tâm thu trên thất (Supraventricular Ectopic Beat — SVPB)',
    aami_code: 'S',
    mitbih_symbols: 'A, a, J, S',
    description: 'Nhịp phát sinh sớm từ vùng trên thất (nhĩ hoặc bộ nối nhĩ-thất), nằm ngoài nút xoang bình thường. Phức bộ QRS thường có hình thái tương tự nhịp xoang (hẹp), nhưng xuất hiện sớm hơn dự kiến. Sóng P có thể thay đổi hình thái hoặc không nhìn thấy rõ.',
    ai_focus: 'Mô hình nhận diện sự xuất hiện sớm bất thường và thay đổi nhỏ trong hình thái sóng P/khoảng PR so với nhịp cơ sở.',
    color: '#f59e0b',
    risk: 'Thấp — Chú ý',
    action: 'Ghi nhận tần suất xuất hiện. Nếu tần suất cao (>6/phút) hoặc thành chuỗi, thông báo bác sĩ.',
  },
  'CẢNH BÁO: NHỊP THẤT (V)': {
    title: 'Ngoại tâm thu thất — PVC (Ventricular Ectopic Beat — VPB)',
    aami_code: 'V',
    mitbih_symbols: 'V, E',
    description: 'Nhịp phát sinh sớm từ tâm thất, nằm ngoài hệ thống dẫn truyền bình thường. Đặc trưng bởi phức bộ QRS dãn rộng (thường >120ms) với hình thái bất thường, không có sóng P đi trước, đoạn ST lệch hướng với phức bộ QRS. Khoảng RR trước và sau nhịp PVC thường bất đều.',
    ai_focus: 'Mô hình tập trung cao vào vùng phức bộ QRS dãn rộng và biến dạng (vùng màu đỏ đậm trên heatmap). Đây là đặc trưng chính phân biệt PVC với nhịp xoang.',
    color: '#ef4444',
    risk: 'Trung bình-Cao — Khẩn cấp',
    action: 'Đánh giá ngay tần suất PVC. PVC đa ổ, chuỗi đôi (bigeminy/trigeminy), hoặc nhịp chạy ≥3 PVC liên tiếp cần được bác sĩ đánh giá khẩn cấp.',
  },
  'CẢNH BÁO: HỢP NHẤT (F)': {
    title: 'Nhịp hợp nhất (Fusion Beat — FB)',
    aami_code: 'F',
    mitbih_symbols: 'F',
    description: 'Nhịp hình thành khi 2 xung động (1 từ xoang và 1 từ ổ ngoại vị thất) kết hợp đồng thời tạo nên 1 phức bộ QRS có hình thái trung gian — không hoàn toàn bình thường cũng không giống PVC điển hình. Thường rộng hơn nhịp xoang nhưng hẹp hơn PVC thuần túy.',
    ai_focus: 'Mô hình nhận diện hình thái phức bộ QRS không điển hình — rộng bất thường nhưng không hoàn toàn giống pattern PVC hoặc xoang. Vùng heatmap thường trải rộng hơn so với PVC.',
    color: '#ef4444',
    risk: 'Trung bình-Cao — Khẩn cấp',
    action: 'Báo cáo bác sĩ để đánh giá. Nhịp hợp nhất thường chỉ điểm có ổ ngoại vị thất hoạt động đồng thời với nút xoang.',
  },
  'CẢNH BÁO: CHƯA RÕ (Q)': {
    title: 'Nhịp chưa phân loại (Unknown/Unclassifiable — Q)',
    aami_code: 'Q',
    mitbih_symbols: '/, f, Q',
    description: 'Nhịp không thể phân loại chắc chắn vào 4 nhóm còn lại. Có thể do nhiều nguyên nhân: tín hiệu nhiễu quá nhiều, hình thái QRS không điển hình, hoặc phức bộ bị suy giảm chất lượng trong quá trình thu thập. Cũng có thể là nhịp rung thất/cuồng nhĩ trong những giai đoạn hình thái QRS biến mất gần như hoàn toàn.',
    ai_focus: 'Mô hình không tìm được pattern đặc trưng rõ ràng, nhưng phát hiện tín hiệu không phù hợp với nhịp xoang bình thường. Phân phối xác suất thường phân tán giữa nhiều lớp.',
    color: '#f59e0b',
    risk: 'Không xác định — Cần đánh giá',
    action: 'Kiểm tra lại chất lượng tín hiệu ECG (điện cực, nhiễu). Nếu tín hiệu tốt mà vẫn Q — báo bác sĩ đánh giá trực tiếp.',
  },
};

/**
 * Lấy giải thích lâm sàng theo nhãn.
 * @param {string} prediction — nhãn từ WS/AnomalyContext
 * @returns {object|null}
 */
export const getClinicalExplanation = (prediction) => {
  if (!prediction) return null;
  return CLINICAL_EXPLANATIONS[prediction] ?? null;
};
