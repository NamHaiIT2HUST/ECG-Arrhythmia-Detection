import pytest
from starlette.websockets import WebSocketDisconnect

from tests.conftest import requires_physionet_data, requires_saved_model

EXPECTED_PAYLOAD_KEYS = {
    "chunk", "prediction", "heatmap", "latency_ms", "confidence",
    "bpm", "hrv_sdnn", "hrv_rmssd", "latency_e2e_ms", "is_new_beat",
    "afib_suspected", "afib_score", "tachycardia_suspected",
}


def _ticket(client, auth_headers, role="nurse"):
    res = client.post("/api/auth/ws-ticket", headers=auth_headers[role])
    return res.json()["ticket"]


@requires_physionet_data
@requires_saved_model
def test_ws_ecg_payload_schema(client, auth_headers):
    ticket = _ticket(client, auth_headers)
    with client.websocket_connect(f"/ws/ecg?record=100&ticket={ticket}") as ws:
        data = ws.receive_json()

    assert EXPECTED_PAYLOAD_KEYS.issubset(data.keys()), f"Thiếu field trong payload: {EXPECTED_PAYLOAD_KEYS - data.keys()}"
    assert isinstance(data["chunk"], list)
    assert len(data["chunk"]) == 10
    assert isinstance(data["is_new_beat"], bool)


@requires_physionet_data
@requires_saved_model
def test_ws_ecg_invalid_record_falls_back_to_default(client, auth_headers):
    """record_exists() phải chặn record không tồn tại và tự dùng bản ghi mặc định
    (xem backend/api/records_routes.py) thay vì làm sập kết nối."""
    ticket = _ticket(client, auth_headers)
    with client.websocket_connect(f"/ws/ecg?record=khong_ton_tai_999&ticket={ticket}") as ws:
        data = ws.receive_json()
    assert "chunk" in data


def test_ws_ecg_requires_login(client):
    """Du lieu ECG real-time la du lieu benh nhan nhay cam - khong duoc phep ket noi neu
    thieu/sai access token (xem backend/core/security.get_user_from_token)."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/ecg?record=100"):
            pass
    assert exc_info.value.code == 4401

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/ecg?record=100&ticket=token-gia-mao"):
            pass
    assert exc_info.value.code == 4401
