"""Helper nho de chay inference qua ONNX Runtime, dung chung cho validate_onnx_classification.py.
KHONG dung Grad-CAM (ONNX Runtime khong ho tro backward pass) - chi de danh gia do chinh xac
phan loai cua ban ONNX so voi ban PyTorch goc."""
import numpy as np
import onnxruntime as ort

from backend.core.signal_processing import normalize_window
from backend.service.inference_service import AAMI_CLASSES


class ONNXPredictor:
    def __init__(self, onnx_path: str):
        self.session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])

    def predict(self, beat_window) -> str:
        """Nhan 1 nhip (187 diem, DA loc nhieu + can dinh R + resample - giong het hop dong
        cua ai_service.predict()), tra ve nhan AAMI dang chu."""
        x = normalize_window(beat_window).reshape(1, 1, -1).astype(np.float32)
        logits = self.session.run(None, {"input": x})[0]
        pred_class = int(np.argmax(logits, axis=1)[0])
        return AAMI_CLASSES.get(pred_class, "KHÔNG XÁC ĐỊNH")
