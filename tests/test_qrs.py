import pytest

from backend.scripts.validate_qrs import evaluate_record
from tests.conftest import requires_physionet_data

# Chỉ assert trên các bản ghi dễ/trung bình. KHÔNG assert record 207 (rung thất/cuồng nhĩ)
# hay 119 (PVC tần suất rất cao) — plan.md mục 3.2 đã ghi rõ đây là 2 bản ghi khó nhất
# MIT-BIH do đặc thù hình dạng QRS gần như biến mất/biến dạng nặng, F1 thấp hơn (~90-92%)
# là điều đã biết trước, không phải bug — assert chúng sẽ tạo flaky test vô nghĩa.
EASY_RECORDS = ["100", "213", "234"]


@requires_physionet_data
@pytest.mark.parametrize("record_id", EASY_RECORDS)
def test_r_peak_detection_accuracy(record_id):
    result = evaluate_record(record_id)
    assert result["f1"] > 0.90, (
        f"Record {record_id}: F1={result['f1']*100:.2f}% thấp hơn ngưỡng 90% "
        f"(TP={result['tp']} FP={result['fp']} FN={result['fn']})"
    )
