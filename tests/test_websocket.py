from tests.conftest import requires_physionet_data, requires_saved_model

EXPECTED_PAYLOAD_KEYS = {
    "chunk", "prediction", "heatmap", "latency_ms", "confidence",
    "bpm", "hrv_sdnn", "hrv_rmssd", "is_new_beat",
}


@requires_physionet_data
@requires_saved_model
def test_ws_ecg_payload_schema(client):
    with client.websocket_connect("/ws/ecg?record=100") as ws:
        data = ws.receive_json()

    assert EXPECTED_PAYLOAD_KEYS.issubset(data.keys()), f"Thiếu field trong payload: {EXPECTED_PAYLOAD_KEYS - data.keys()}"
    assert isinstance(data["chunk"], list)
    assert len(data["chunk"]) == 10
    assert isinstance(data["is_new_beat"], bool)


@requires_physionet_data
@requires_saved_model
def test_ws_ecg_invalid_record_falls_back_to_default(client):
    """record_exists() phải chặn record không tồn tại và tự dùng bản ghi mặc định
    (xem backend/api/records_routes.py) thay vì làm sập kết nối."""
    with client.websocket_connect("/ws/ecg?record=khong_ton_tai_999") as ws:
        data = ws.receive_json()
    assert "chunk" in data
