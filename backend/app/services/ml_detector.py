"""
ML Detector Service — PixelProof
=================================
Integration for the trained EfficientNet-B0 image forensics model
(backend/app/models/image_forensics_model.pth) trained on CASIA 2.0.

Architecture:
  - Base:          torchvision.models.efficientnet_b0(weights=None)
  - Classifier:    Dropout(0.4) → Linear(1280, 256) → ReLU → Dropout(0.3) → Linear(256, 2)
  - Input:         PIL RGB → Resize(224×224) → ToTensor → Normalize(ImageNet mean/std)
  - Output:        2-class raw logits → softmax → [authentic_probability, manipulated_probability]
  - Class map:     index 0 = Authentic, index 1 = Manipulated
  - Weights file:  backend/app/models/image_forensics_model.pth (state_dict)

Held-out test results (70/15/15 split, 1,893 test images):
  - Accuracy:  0.6962
  - Precision: 0.5942
  - Recall:    0.7958
  - F1 Score:  0.6804
  - ROC-AUC:   0.7636

CRITICAL:
  ML output is a probabilistic classification signal, NOT definitive proof that
  an image is authentic or manipulated. It must be interpreted alongside forensic evidence.
"""

import os
import hashlib
import logging
from typing import Optional, Dict, Any

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants matching training exactly
# ---------------------------------------------------------------------------
IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
CLASS_NAMES = ["authentic", "manipulated"]
MODEL_NAME = "EfficientNet-B0"
MODEL_VERSION = "pixelproof-casia-v1"

# Held-out benchmark metrics (honest measured values from Colab evaluation)
HELD_OUT_METRICS = {
    "accuracy": 0.6962,
    "precision": 0.5942,
    "recall": 0.7958,
    "f1_score": 0.6804,
    "roc_auc": 0.7636,
    "train_images": 8829,
    "validation_images": 1892,
    "held_out_test_images": 1893,
    "dataset": "CASIA 2.0 (70/15/15 split)",
    "positive_class": "manipulated"
}


class MLDetectorService:
    """
    Singleton service for the EfficientNet-B0 image forensics classifier.
    Loads model weights once on startup, manages evaluation mode and CPU/MPS/CUDA inference.
    """

    DEFAULT_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    DEFAULT_WEIGHTS_ENV = "PIXELPROOF_MODEL_PATH"
    PRIMARY_WEIGHTS_FILE = "image_forensics_model.pth"

    def __init__(self):
        self._model = None
        self.weights_path: Optional[str] = None
        self._transform = None
        self._device = None
        self.load_error: Optional[str] = None
        self._load_attempted: bool = False
        self.metadata: Dict[str, Any] = self._default_metadata()
        # Note: Model loading is intentionally deferred to avoid blocking startup or port binding.

    @property
    def model(self):
        """Lazy model property: loads EfficientNet-B0 on first demand if not yet loaded."""
        if self._model is None and not self._load_attempted and self.load_error is None:
            self.ensure_loaded()
        return self._model

    @model.setter
    def model(self, val):
        self._model = val

    def _default_metadata(self) -> Dict[str, Any]:
        """Returns standard metadata schema with real held-out metrics."""
        return {
            "model": MODEL_NAME,
            "model_version": MODEL_VERSION,
            "architecture": "torchvision.models.efficientnet_b0 (custom 2-class classifier head)",
            "classifier_head": "Dropout(0.4) → Linear(1280, 256) → ReLU → Dropout(0.3) → Linear(256, 2)",
            "classes": {0: "authentic", 1: "manipulated"},
            "input_size": [IMG_SIZE, IMG_SIZE],
            "color_format": "RGB",
            "normalization": {"mean": IMAGENET_MEAN, "std": IMAGENET_STD},
            "metrics": HELD_OUT_METRICS,
            "model_hash_sha256": None,
            "device": None,
            "status": "UNLOADED",
            "status_note": "Awaiting on-demand initialization.",
        }

    def _find_weights_path(self) -> Optional[str]:
        """Locates candidate weights file on disk without performing any model loading."""
        candidate = os.environ.get(self.DEFAULT_WEIGHTS_ENV)
        if candidate and os.path.isfile(candidate):
            return candidate
        if os.path.exists(self.DEFAULT_MODEL_DIR):
            primary = os.path.join(self.DEFAULT_MODEL_DIR, self.PRIMARY_WEIGHTS_FILE)
            if os.path.isfile(primary):
                return primary
            for fname in sorted(os.listdir(self.DEFAULT_MODEL_DIR)):
                if fname.endswith((".pth", ".pt")):
                    cand = os.path.join(self.DEFAULT_MODEL_DIR, fname)
                    if os.path.isfile(cand):
                        return cand
        return None

    def is_available(self) -> bool:
        """
        Returns True if the PyTorch model is loaded or ready for on-demand lazy inference.
        Fast non-blocking check: does NOT import PyTorch or load weights into RAM,
        allowing /api/health and FastAPI startup to bind to the port immediately.
        """
        if self._model is not None:
            return True
        if self.load_error is not None:
            return False
        path = self._find_weights_path()
        return path is not None and os.path.isfile(path)

    def ensure_loaded(self) -> bool:
        """
        Lazily loads weights and builds the singleton EfficientNet-B0 model on first demand.
        Caches the model so all subsequent analyses reuse the same instance.
        """
        if self._model is not None:
            return True
        if self.load_error is not None:
            return False

        self._load_attempted = True
        candidate = self._find_weights_path()
        if candidate and os.path.isfile(candidate):
            return self.load_weights(candidate)
        else:
            self.load_error = f"Model weights file not found in {self.DEFAULT_MODEL_DIR}"
            self.metadata["status"] = "NOT_FOUND"
            self.metadata["status_note"] = self.load_error
            return False

    @staticmethod
    def _build_model():
        """Constructs EfficientNet-B0 matching training architecture."""
        import torch.nn as nn
        from torchvision import models

        m = models.efficientnet_b0(weights=None)
        in_features = m.classifier[1].in_features  # 1280
        m.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(256, 2)
        )
        return m

    def _build_transform(self):
        """Constructs torchvision inference transform matching training."""
        from torchvision import transforms

        self._transform = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])

    def get_metadata(self) -> Dict[str, Any]:
        """Returns model specification, training provenance, and honest test metrics."""
        return self.metadata.copy()

    def _select_device(self):
        """Selects computation device: CUDA > MPS > CPU with CPU fallback guarantee."""
        import torch
        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():
            try:
                # Sanity check MPS on small tensor
                _ = torch.zeros(1, device="mps")
                return torch.device("mps")
            except Exception:
                return torch.device("cpu")
        return torch.device("cpu")

    def load_weights(self, weights_path: str) -> bool:
        """
        Loads weights from PyTorch .pth file.
        Safely supports CPU automatically, and falls back to CPU if hardware acceleration fails.
        """
        if not os.path.isfile(weights_path):
            self.load_error = f"Weights file does not exist: {weights_path}"
            self.metadata["status"] = "FILE_NOT_FOUND"
            self.metadata["status_note"] = self.load_error
            return False

        try:
            import torch

            self._device = self._select_device()

            # Compute SHA-256 for integrity & provenance
            hasher = hashlib.sha256()
            with open(weights_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            weights_sha256 = hasher.hexdigest()

            # Load weights with map_location
            try:
                raw = torch.load(weights_path, map_location=self._device, weights_only=False)
            except Exception as device_err:
                logger.warning("Failed to load on %s (%s). Falling back to CPU.", self._device, device_err)
                self._device = torch.device("cpu")
                raw = torch.load(weights_path, map_location=self._device, weights_only=False)

            # Determine if raw state_dict or checkpoint dict
            state_dict = None
            if isinstance(raw, dict) and "model_state_dict" in raw:
                state_dict = raw["model_state_dict"]
            elif isinstance(raw, dict):
                state_dict = raw
            else:
                self.load_error = f"Unexpected .pth content type: {type(raw).__name__}"
                self.metadata["status"] = "LOAD_ERROR"
                self.metadata["status_note"] = self.load_error
                return False

            # Build architecture and load state_dict
            model = self._build_model()
            model.load_state_dict(state_dict)
            del raw, state_dict  # Immediately release raw deserialized state_dict from memory
            
            # On CPU, constrain thread pool to prevent excessive OpenMP thread stack memory
            if self._device.type == "cpu":
                try:
                    torch.set_num_threads(1)
                except Exception:
                    pass

            model = model.to(self._device)
            model.eval()

            self.model = model
            self.weights_path = weights_path
            self._build_transform()
            self.load_error = None

            import gc
            gc.collect()  # Flush startup loading objects

            self.metadata["model_hash_sha256"] = weights_sha256
            self.metadata["device"] = str(self._device)
            self.metadata["status"] = "LOADED"
            self.metadata["status_note"] = (
                f"Model loaded successfully from {os.path.basename(weights_path)} "
                f"on {str(self._device)}."
            )

            logger.info("EfficientNet-B0 forensics model loaded successfully on %s", self._device)
            return True

        except ImportError as e:
            self.model = None
            self.load_error = f"PyTorch dependency missing: {str(e)}"
            self.metadata["status"] = "DEPENDENCY_MISSING"
            self.metadata["status_note"] = self.load_error
            logger.warning("ML detector unavailable: %s", self.load_error)
            return False

        except Exception as e:
            self.model = None
            self.load_error = f"Failed to load model weights: {str(e)}"
            self.metadata["status"] = "LOAD_ERROR"
            self.metadata["status_note"] = self.load_error
            logger.exception("Failed to load ML weights: %s", e)
            return False

    def predict(
        self,
        pil_img: Optional[Image.Image] = None,
        cv_bgr: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Executes ML inference on the input image.

        Prediction mapping:
          argmax 0 => "authentic"
          argmax 1 => "manipulated"

        Returns structured dictionary with:
          - available: bool
          - prediction: "authentic" | "manipulated" | None
          - authentic_probability: float
          - manipulated_probability: float
          - confidence: float (probability of the selected ML class)
          - model: "EfficientNet-B0"
          - model_version: "pixelproof-casia-v1"
          - explanation: signal explanation
          - disclaimer: honest probabilistic notice
        """
        if not self.ensure_loaded():
            return {
                "available": False,
                "prediction": None,
                "authentic_probability": None,
                "manipulated_probability": None,
                "confidence": None,
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "explanation": self.load_error or "ML model is not loaded.",
                "disclaimer": "ML classification is unavailable.",
                "metrics": HELD_OUT_METRICS,
                "device": None,
                # Backward-compatibility aliases
                "authentic_prob": None,
                "manipulated_prob": None,
            }

        try:
            import torch

            # 1. Image preprocessing and format handling
            if pil_img is not None:
                img = pil_img.convert("RGB")
            elif cv_bgr is not None:
                import cv2
                rgb = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
            else:
                return {
                    "available": True,
                    "prediction": None,
                    "authentic_probability": None,
                    "manipulated_probability": None,
                    "confidence": None,
                    "model": MODEL_NAME,
                    "model_version": MODEL_VERSION,
                    "explanation": "No image data provided for ML inference.",
                    "disclaimer": "ML output is a probabilistic classification signal and should be interpreted alongside forensic evidence.",
                    "metrics": HELD_OUT_METRICS,
                    "device": str(self._device),
                    "authentic_prob": None,
                    "manipulated_prob": None,
                }

            # Preprocess: Resize(224x224) -> ToTensor() -> Normalize(ImageNet)
            tensor = self._transform(img).unsqueeze(0).to(self._device)

            # 2. Forward pass with inference_mode (no gradients, minimal memory)
            with torch.inference_mode():
                try:
                    logits = self.model(tensor)
                except Exception as run_err:
                    # Fallback to CPU if device-specific execution fails
                    if self._device.type != "cpu":
                        logger.warning("Inference failed on %s (%s). Retrying on CPU.", self._device, run_err)
                        self._device = torch.device("cpu")
                        self.model = self.model.to(self._device)
                        tensor = tensor.to(self._device)
                        logits = self.model(tensor)
                    else:
                        raise run_err

                probs = torch.softmax(logits, dim=1)[0]
                auth_prob = round(float(probs[0].item()), 4)
                manip_prob = round(float(probs[1].item()), 4)

            # Explicitly release prediction tensors
            del logits, probs, tensor

            # argmax class 0 => authentic, argmax class 1 => manipulated
            if manip_prob > auth_prob:
                prediction = "manipulated"
                signal_label = "Manipulation-Leaning ML Signal"
                confidence = manip_prob
                explanation = "Model detected visual patterns more consistent with manipulated imagery."
            else:
                prediction = "authentic"
                signal_label = "Authenticity-Leaning ML Signal"
                confidence = auth_prob
                explanation = "Model detected visual patterns more consistent with authentic imagery."

            # 3. Memory-safe Grad-CAM Influence Map Generation
            gradcam_res = self.generate_gradcam(
                img,
                target_class_idx=1 if manip_prob > auth_prob else 0
            )

            return {
                "available": True,
                "prediction": prediction,
                "signal_label": signal_label,
                "authentic_probability": auth_prob,
                "manipulated_probability": manip_prob,
                "confidence": round(confidence, 4),
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "explanation": explanation,
                "disclaimer": "This is an independent machine-learning signal, not the final forensic conclusion.",
                "signal_type": "Independent ML Signal",
                "score_added": 0,
                "gradcam": gradcam_res,
                "metrics": HELD_OUT_METRICS,
                "device": str(self._device),
                # Backward-compatibility aliases
                "authentic_prob": auth_prob,
                "manipulated_prob": manip_prob,
            }

        except Exception as e:
            logger.exception("ML inference error: %s", e)
            return {
                "available": False,
                "prediction": None,
                "authentic_probability": None,
                "manipulated_probability": None,
                "confidence": None,
                "model": MODEL_NAME,
                "model_version": MODEL_VERSION,
                "explanation": f"ML model inference encountered an error: {str(e)}",
                "disclaimer": "ML classification failed for this image.",
                "gradcam": {
                    "available": False,
                    "target_class": None,
                    "visualization": None,
                    "explanation": "ML inference failed."
                },
                "metrics": HELD_OUT_METRICS,
                "device": str(self._device) if self._device else None,
                "authentic_prob": None,
                "manipulated_prob": None,
            }

    def generate_gradcam(
        self,
        img_pil: Image.Image,
        target_class_idx: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Computes Grad-CAM model influence visualization on EfficientNet-B0's final feature layer.
        Memory-safe implementation:
        - Uses the SAME EfficientNet model instance.
        - Hooks are registered and strictly removed in a finally block.
        - Parameter gradients are wiped with zero_grad(set_to_none=True).
        - Computes overlay at display thumbnail resolution (<= 640px) to prevent array explosion.
        - Gracefully degrades with an honest reason on any memory pressure or execution error.
        Does NOT alter model weights or inference probabilities.
        """
        if not self.ensure_loaded():
            return {
                "available": False,
                "target_class": None,
                "visualization": None,
                "explanation": self.load_error or "Grad-CAM unavailable because ML model is not loaded."
            }

        handle_f = None
        handle_b = None
        try:
            import torch
            import cv2
            from app.utils.image_utils import encode_cv2_to_base64_data_uri

            model = self.model
            target_layer = model.features[-1]

            activations = []
            gradients = []

            def forward_hook(module, inp, out):
                activations.append(out)

            def backward_hook(module, grad_in, grad_out):
                gradients.append(grad_out[0])

            handle_f = target_layer.register_forward_hook(forward_hook)
            handle_b = target_layer.register_full_backward_hook(backward_hook)

            tensor = self._transform(img_pil.convert("RGB")).unsqueeze(0).to(self._device)
            tensor.requires_grad_(True)

            model.zero_grad(set_to_none=True)
            logits = model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

            if target_class_idx is None:
                target_class_idx = int(torch.argmax(probs).item())

            score = logits[0, target_class_idx]
            score.backward()

            # Clean up hooks immediately
            if handle_f is not None:
                handle_f.remove()
                handle_f = None
            if handle_b is not None:
                handle_b.remove()
                handle_b = None

            if not activations or not gradients:
                return {
                    "available": False,
                    "target_class": CLASS_NAMES[target_class_idx],
                    "visualization": None,
                    "explanation": "Feature activations could not be extracted for Grad-CAM."
                }

            act = activations[0].detach()    # [1, 1280, 7, 7]
            grad = gradients[0].detach()     # [1, 1280, 7, 7]
            del activations, gradients

            weights = torch.mean(grad, dim=(2, 3), keepdim=True)  # [1, 1280, 1, 1]
            del grad
            cam = torch.sum(weights * act, dim=1, keepdim=True)    # [1, 1, 7, 7]
            del weights, act
            cam = torch.relu(cam)

            cam_np = cam[0, 0].cpu().numpy()
            del cam, logits, probs, tensor
            
            # Wiping parameter gradients frees all cached autograd graph and parameter .grad tensors
            model.zero_grad(set_to_none=True)

            max_c = float(np.max(cam_np))
            min_c = float(np.min(cam_np))
            if max_c > min_c:
                cam_norm = ((cam_np - min_c) / (max_c - min_c) * 255.0).astype(np.uint8)
            else:
                cam_norm = np.zeros_like(cam_np, dtype=np.uint8)
            del cam_np

            # Memory optimization: Grad-CAM spatial resolution is 7x7.
            # Render overlay at thumbnail resolution (max 640px) to prevent 45 MB uncompressed arrays.
            orig_w, orig_h = img_pil.size
            max_overlay_dim = 640
            if max(orig_w, orig_h) > max_overlay_dim:
                scale_d = max_overlay_dim / float(max(orig_w, orig_h))
                disp_w = max(16, int(round(orig_w * scale_d)))
                disp_h = max(16, int(round(orig_h * scale_d)))
                disp_pil = img_pil.resize((disp_w, disp_h), Image.Resampling.BILINEAR)
            else:
                disp_w, disp_h = orig_w, orig_h
                disp_pil = img_pil

            cam_resized = cv2.resize(cam_norm, (disp_w, disp_h), interpolation=cv2.INTER_CUBIC)
            del cam_norm
            heatmap = cv2.applyColorMap(cam_resized, cv2.COLORMAP_JET)
            del cam_resized

            disp_rgb = np.array(disp_pil.convert("RGB"))
            if disp_pil is not img_pil:
                del disp_pil
            disp_bgr = cv2.cvtColor(disp_rgb, cv2.COLOR_RGB2BGR)
            del disp_rgb

            cam_overlay = cv2.addWeighted(disp_bgr, 0.55, heatmap, 0.45, 0)
            del disp_bgr, heatmap

            vis_uri = encode_cv2_to_base64_data_uri(cam_overlay, "png", max_dim=640)
            del cam_overlay

            target_name = CLASS_NAMES[target_class_idx]
            return {
                "available": True,
                "target_class": target_name,
                "visualization": vis_uri,
                "explanation": (
                    f"Model attention/influence visualization for '{target_name}' classification. "
                    "Highlighted regions contributed more strongly to the model's selected classification. "
                    "This does not identify confirmed manipulated pixels."
                )
            }
        except Exception as e:
            logger.warning("Grad-CAM generation failed: %s", e)
            return {
                "available": False,
                "target_class": None,
                "visualization": None,
                "explanation": f"Grad-CAM influence map generation was skipped for memory safety: {str(e)}"
            }
        finally:
            if handle_f is not None:
                try:
                    handle_f.remove()
                except Exception:
                    pass
            if handle_b is not None:
                try:
                    handle_b.remove()
                except Exception:
                    pass
            if self.model is not None:
                try:
                    self.model.zero_grad(set_to_none=True)
                except Exception:
                    pass


# Singleton instance loaded once across the application lifecycle
ml_detector = MLDetectorService()
