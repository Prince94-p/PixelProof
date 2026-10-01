# PixelProof Machine Learning Model Specifications

This directory houses the optional deep learning tampering detection model weights for PixelProof.

---

## 1. Model Artifact Specifications

- **Expected Filename:** `image_forensics_model.pth`
- **Expected Directory Location:** `backend/app/models/image_forensics_model.pth`
- **Architecture:** `EfficientNet-B0` (`torchvision.models.efficientnet_b0`)
- **Classifier Head:**
  ```python
  nn.Sequential(
      nn.Dropout(p=0.3, inplace=True),
      nn.Linear(1280, 2)
  )
  ```
- **Classes:**
  - Index `0`: `authentic`
  - Index `1`: `manipulated`
- **Model Version Identifier:** `pixelproof-casia-v1`

---

## 2. Preprocessing Pipeline

All inputs are converted to RGB color space and transformed using standard ImageNet normalization:
```python
transforms.Compose([
    transforms.Resize((224, 224), interpolation=transforms.InterpolationMode.BILINEAR),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

---

## 3. Training & Benchmark Performance (CASIA 2.0)

The model was fine-tuned on the CASIA 2.0 image tampering dataset (splicing and copy-move manipulations).

### Held-out Test Set Performance (1,893 Test Images)
- **Accuracy:** 69.62%
- **Precision:** 59.42%
- **Recall:** 79.58%
- **F1 Score:** 68.04%
- **ROC-AUC:** 76.36%

*Note: These metrics evaluate benchmark generalization on CASIA 2.0 test images. They do not represent per-image confidence on in-the-wild or AI-generated imagery.*

---

## 4. Architectural Non-Negotiables & Signal Independence

1. **Independent Forensic Signal:** The ML classification output is strictly independent and is **NEVER** added to the classical 0–100 forensic score (`score_added = 0`).
2. **Not an AI-Generated Image Detector:** This model detects traditional digital manipulation artifacts (splicing, cloning, seam carving), not generative diffusion or GAN synthesis.
3. **Scientific Explainability (Grad-CAM):** Visual influence heatmaps are computed using Gradient-weighted Class Activation Mapping (Grad-CAM) targeting `model.features[-1]` without modifying model state or inference outputs.

---

## 5. Graceful Fallback Behavior

If `image_forensics_model.pth` is missing or fails to initialize:
- `ml_detector.is_available()` returns `False`.
- The full 5-module classical forensic engine continues functioning with zero degradation.
- API responses include `ml_analysis.available = false` with explanatory fallback notes.
- The `.pth` weight file is ignored by git to protect repository portability.
