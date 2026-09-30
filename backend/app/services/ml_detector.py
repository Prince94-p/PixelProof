import os
import hashlib
import json
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image

class MLDetectorService:
    """
    Service interface for an optional trained machine learning / deep learning model
    (e.g., PyTorch .pt/.pth, ONNX, or TorchScript) developed separately for image tampering detection.
    
    If no trained weights file is present in the environment or model directory:
    - Does NOT fake predictions or fabricate confidence numbers.
    - Returns available: False.
    - Contributes 0 points to the forensic suspicion score.
    - Exposes genuine model metadata fields (architecture, datasets, verified evaluation metrics).
    """

    DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    DEFAULT_WEIGHTS_ENV = "PIXELPROOF_MODEL_PATH"
    DEFAULT_META_ENV = "PIXELPROOF_MODEL_META_PATH"

    def __init__(self):
        self.model = None
        self.model_backend = None  # 'onnx', 'torch', or None
        self.weights_path: Optional[str] = None
        self.metadata: Dict[str, Any] = self._default_metadata()
        self._initialize()

    def _default_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata schema. Only genuinely measured metrics are reported."""
        return {
            "model_name": None,
            "model_version": None,
            "architecture": None,
            "dataset_names": [],
            "train_samples": None,
            "validation_samples": None,
            "test_samples": None,
            "input_size": None,
            "test_accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None,
            "roc_auc": None,
            "decision_threshold": None,
            "model_hash_sha256": None,
            "status": "UNLOADED",
            "status_note": (
                "No trained weights file loaded. Plug-and-play adapter ready for "
                ".pt, .pth, or .onnx models once training and evaluation are complete."
            )
        }

    def _initialize(self):
        """Checks environment variables and model directory for valid exported weights."""
        candidate_path = os.environ.get(self.DEFAULT_WEIGHTS_ENV)
        
        # Check default models directory if not explicitly in env
        if not candidate_path and os.path.exists(self.DEFAULT_MODEL_DIR):
            for fname in os.listdir(self.DEFAULT_MODEL_DIR):
                if fname.endswith((".onnx", ".pt", ".pth")):
                    candidate_path = os.path.join(self.DEFAULT_MODEL_DIR, fname)
                    break

        if candidate_path and os.path.isfile(candidate_path):
            self.load_weights(candidate_path)

    def is_available(self) -> bool:
        """Returns True only if a trained model was successfully loaded into memory."""
        return self.model is not None

    def get_metadata(self) -> Dict[str, Any]:
        """Returns model specification, training provenance, and genuinely calculated benchmark metrics."""
        return self.metadata.copy()

    def load_weights(self, weights_path: str, metadata_path: Optional[str] = None) -> bool:
        """
        Loads an exported model file (.onnx, .pt, .pth).
        Computes SHA-256 hash of the weights file for provenance tracking.
        """
        if not os.path.isfile(weights_path):
            return False

        try:
            # 1. Compute model weight binary hash
            hasher = hashlib.sha256()
            with open(weights_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            weights_sha256 = hasher.hexdigest()

            # 2. Check file format and load backend
            if weights_path.endswith(".onnx"):
                try:
                    import onnxruntime as ort
                    self.model = ort.InferenceSession(weights_path)
                    self.model_backend = "onnx"
                except ImportError:
                    # ONNX Runtime not installed in minimal venv
                    self.model = None
                    self.metadata["status"] = "BACKEND_DEPENDENCY_MISSING"
                    self.metadata["status_note"] = "Found .onnx file but 'onnxruntime' is not installed in the python environment."
                    return False
            elif weights_path.endswith((".pt", ".pth")):
                try:
                    import torch
                    self.model = torch.jit.load(weights_path) if weights_path.endswith(".pt") else torch.load(weights_path, map_location="cpu")
                    if hasattr(self.model, "eval"):
                        self.model.eval()
                    self.model_backend = "torch"
                except ImportError:
                    self.model = None
                    self.metadata["status"] = "BACKEND_DEPENDENCY_MISSING"
                    self.metadata["status_note"] = "Found PyTorch weights but 'torch' is not installed in the python environment."
                    return False
            else:
                return False

            self.weights_path = weights_path
            self.metadata["model_hash_sha256"] = weights_sha256
            self.metadata["status"] = "LOADED"
            self.metadata["status_note"] = f"Model loaded from {os.path.basename(weights_path)} using {self.model_backend} runtime."

            # 3. Load companion metadata JSON if available
            meta_file = metadata_path or os.environ.get(self.DEFAULT_META_ENV) or (os.path.splitext(weights_path)[0] + "_metadata.json")
            if os.path.isfile(meta_file):
                try:
                    with open(meta_file, "r") as mf:
                        loaded_meta = json.load(mf)
                    for k in self.metadata:
                        if k in loaded_meta:
                            self.metadata[k] = loaded_meta[k]
                except Exception:
                    pass

            return True

        except Exception as e:
            self.model = None
            self.metadata["status"] = "LOAD_ERROR"
            self.metadata["status_note"] = f"Failed to load weights: {str(e)}"
            return False

    def predict(self, pil_img: Optional[Image.Image] = None, cv_bgr: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Executes inference if model is available.
        If no model is loaded: returns available: False with zero score contribution and clear explanation.
        NOTE: ML confidence is explicitly NOT called the probability that the entire image is fake.
        """
        if not self.is_available():
            return {
                "available": False,
                "prediction": None,
                "confidence": None,
                "threshold": None,
                "model_version": self.metadata.get("model_version"),
                "explanation": (
                    "No trained ML model weights loaded. Forensics evaluated strictly via independent "
                    "computer vision, frequency error-level, feature matching, and noise consistency algorithms."
                ),
                "metadata": self.get_metadata()
            }

        # Placeholder inference pipeline for when model is plugged in
        try:
            # When model is loaded: resize, normalize, pass through self.model
            # Note: Do not fabricate confidence; run actual forward pass
            input_h, input_w = self.metadata.get("input_size") or (256, 256)
            resized = pil_img.resize((input_w, input_h), Image.Resampling.BILINEAR)
            img_arr = np.array(resized).astype(np.float32) / 255.0
            # Standard ImageNet normalization: (x - mean) / std
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            norm_arr = (img_arr - mean) / std
            tensor_chw = np.transpose(norm_arr, (2, 0, 1))[np.newaxis, ...]  # 1, C, H, W

            if self.model_backend == "onnx":
                input_name = self.model.get_inputs()[0].name
                raw_out = self.model.run(None, {input_name: tensor_chw})[0]
                prob = float(raw_out[0][0]) if raw_out.ndim > 1 else float(raw_out[0])
            elif self.model_backend == "torch":
                import torch
                with torch.no_grad():
                    t_in = torch.from_numpy(tensor_chw)
                    raw_out = self.model(t_in)
                    if hasattr(torch, "sigmoid"):
                        prob = float(torch.sigmoid(raw_out).squeeze().item())
                    else:
                        prob = float(raw_out.squeeze().item())
            else:
                prob = None

            threshold = float(self.metadata.get("decision_threshold") or 0.50)
            is_flagged = prob >= threshold if prob is not None else None

            return {
                "available": True,
                "prediction": "MANIPULATION_INDICATOR_DETECTED" if is_flagged else "NO_ML_ANOMALY_DETECTED",
                "confidence": round(prob, 4) if prob is not None else None,
                "threshold": threshold,
                "model_version": self.metadata.get("model_version") or "1.0.0",
                "explanation": (
                    f"Model inference completed. Output activation score: {prob:.4f} against operational threshold {threshold:.2f}. "
                    "This represents the model's feature-space anomaly rating, NOT the total probability that the image is fake."
                ),
                "metadata": self.get_metadata()
            }

        except Exception as e:
            return {
                "available": False,
                "prediction": None,
                "confidence": None,
                "threshold": None,
                "model_version": self.metadata.get("model_version"),
                "explanation": f"ML model inference failed: {str(e)}",
                "metadata": self.get_metadata()
            }

# Singleton instance for reuse
ml_detector = MLDetectorService()
