import numpy as np
import torch

from src.models.resnet1d import ResNet1D
from tests.conftest import requires_onnx_model


def test_resnet1d_output_shape():
    model = ResNet1D(in_channels=1, num_classes=5)
    model.eval()
    x = torch.randn(4, 1, 187)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (4, 5)


def test_resnet1d_accepts_2d_input():
    """forward() tự unsqueeze nếu đầu vào thiếu chiều channel (xem resnet1d.py)."""
    model = ResNet1D(in_channels=1, num_classes=5)
    model.eval()
    x = torch.randn(2, 187)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (2, 5)


def test_softmax_sums_to_one():
    model = ResNet1D(in_channels=1, num_classes=5)
    model.eval()
    x = torch.randn(3, 1, 187)
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)
    np.testing.assert_allclose(probs.sum(dim=1).numpy(), np.ones(3), atol=1e-5)


@requires_onnx_model
def test_onnx_matches_pytorch_argmax():
    """Kiểm tra nhanh song song với backend/scripts/validate_onnx_classification.py (CP6.1):
    lớp dự đoán (argmax) của ONNX FP32 phải khớp 100% với PyTorch trên input ngẫu nhiên —
    xem lý do dùng argmax thay vì sai số tuyệt đối logit thô trong plan.md mục 6.1."""
    import onnxruntime as ort

    from src.models.export_onnx import INPUT_SHAPE, ONNX_FP32_PATH, load_pytorch_model

    model = load_pytorch_model()
    session = ort.InferenceSession(ONNX_FP32_PATH, providers=["CPUExecutionProvider"])

    with torch.no_grad():
        for _ in range(20):
            x = torch.randn(*INPUT_SHAPE, dtype=torch.float32)
            torch_out = model(x).numpy()
            onnx_out = session.run(None, {"input": x.numpy()})[0]
            assert np.argmax(torch_out, axis=1)[0] == np.argmax(onnx_out, axis=1)[0]
