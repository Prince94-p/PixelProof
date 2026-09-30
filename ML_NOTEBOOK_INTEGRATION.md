# ML Notebook Integration Report

**Date:** 2026-10-01  
**Notebook:** `image_forensics_detection.ipynb` (Google Colab)  
**Integrated into:** PixelProof — `backend/app/services/ml_detector.py`

---

## 1. Notebook Architecture Summary

| Property | Value |
|---|---|
| **Base Model** | `torchvision.models.efficientnet_b0` (pretrained on ImageNet) |
| **Transfer Learning** | Freeze all layers → unfreeze last feature block → replace classifier head |
| **Classifier Head** | `Dropout(0.4) → Linear(1280, 256) → ReLU → Dropout(0.3) → Linear(256, 2)` |
| **Output** | 2-class raw logits → `torch.softmax(logits, dim=1)` → `[authentic_prob, manipulated_prob]` |
| **Loss** | `nn.CrossEntropyLoss` with inverse-frequency class weights |
| **Optimizer** | `Adam(lr=1e-3, weight_decay=1e-4)` |
| **Scheduler** | `ReduceLROnPlateau(mode='min', factor=0.5, patience=3)` |
| **Early Stopping** | Patience = 7 epochs |
| **Epochs** | Up to 20 |
| **Batch Size** | 32 |
| **Dataset** | CASIA2 (Au / Tp folders) |
| **Split** | 70% train / 15% validation / 15% test (stratified) |

---

## 2. Preprocessing Contract

### Training (augmented)
```
Resize(256x256) → RandomCrop(224) → RandomHorizontalFlip(0.5) → RandomVerticalFlip(0.2)
→ ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05)
→ RandomRotation(15deg) → ToTensor → Normalize(ImageNet mean/std)
```

### Inference (no augmentation)
```
Resize(224x224) → ToTensor → Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
```

| Parameter | Value |
|---|---|
| **Input size** | 224 x 224 pixels |
| **Color format** | RGB (via `PIL.Image.convert('RGB')`) |
| **Normalization** | ImageNet mean = `[0.485, 0.456, 0.406]`, std = `[0.229, 0.224, 0.225]` |
| **Tensor shape** | `[1, 3, 224, 224]` (batch x channels x H x W) |

---

## 3. Class Mapping

| Index | Class Name | Notebook Label |
|---|---|---|
| **0** | Authentic | `au`, `authentic`, `real`, `original` |
| **1** | Manipulated | `tp`, `tampered`, `fake`, `manipulated` |

**Decision rule:**  
`manipulated_prob >= threshold (default 0.5)` → **MANIPULATED**  
Otherwise → **AUTHENTIC**

The confidence value equals `manipulated_prob` if classified as MANIPULATED, or `authentic_prob` if classified as AUTHENTIC.

---

## 4. Model File Formats

The notebook produces two files:

| File | Format | Contents |
|---|---|---|
| `image_forensics_model.pth` | `torch.save(model.state_dict(), ...)` | Weights only (~16-20 MB) — **primary file for inference** |
| `image_forensics_checkpoint.pth` | `torch.save({dict}, ...)` | Weights + architecture name + class names + normalization constants + training history + test metrics |

### Checkpoint dict keys:
```python
{
    'model_state_dict':   OrderedDict(...),
    'model_architecture': 'efficientnet_b0',
    'num_classes':        2,
    'class_names':        ['Authentic', 'Manipulated'],
    'img_size':           224,
    'imagenet_mean':      [0.485, 0.456, 0.406],
    'imagenet_std':       [0.229, 0.224, 0.225],
    'training_history':   {...},
    'test_metrics': {
        'accuracy':  float,
        'precision': float,
        'recall':    float,
        'f1':        float,
        'roc_auc':   float,
    },
    'disclaimer': 'Predictions are probabilistic estimates, not definitive verdicts.'
}
```

---

## 5. What Was Changed in PixelProof

### Modified file: `backend/app/services/ml_detector.py`

| Change | Detail |
|---|---|
| **Architecture builder** | Added `_build_model()` that constructs the exact EfficientNet-B0 + custom classifier head |
| **Weight loading** | Now handles both `state_dict`-only and full checkpoint dict formats |
| **Preprocessing** | Uses `torchvision.transforms` pipeline (Resize→ToTensor→Normalize) matching notebook exactly |
| **Inference** | Uses `torch.softmax(logits, dim=1)` for 2-class output (was incorrectly using sigmoid) |
| **Class indices** | Correctly maps index 0 → Authentic, index 1 → Manipulated |
| **Metadata** | Now includes architecture, classifier head, class names, normalization params, and test metrics from checkpoint |
| **Response shape** | Added `authentic_prob` and `manipulated_prob` fields alongside existing `confidence` |
| **Backward compat** | All existing keys (`available`, `prediction`, `confidence`, `threshold`, `explanation`, `metadata`) preserved |

### Modified file: `backend/requirements.txt`

Added `torch` and `torchvision` as commented optional dependencies.

### Unchanged files (NOT modified):

- `backend/app/routes/analysis.py` — no changes needed, reads same keys
- `backend/app/services/scoring_engine.py` — no changes needed
- `backend/app/services/ela_analyzer.py` — untouched
- `backend/app/services/copy_move_detector.py` — untouched
- `backend/app/services/noise_analyzer.py` — untouched
- `backend/app/services/metadata_analyzer.py` — untouched
- `backend/app/services/file_analyzer.py` — untouched
- All frontend code — untouched

---

## 6. Files Still Required From Teammate

The trained model weights **do not exist** on this machine. The model must be trained
in the Colab notebook and the output `.pth` files downloaded.

### Required file (minimum):

| File | Place it at |
|---|---|
| **`image_forensics_model.pth`** | `backend/app/models/image_forensics_model.pth` |

### Optional but recommended:

| File | Place it at | Benefit |
|---|---|---|
| `image_forensics_checkpoint.pth` | `backend/app/models/image_forensics_checkpoint.pth` | Auto-populates test metrics (accuracy, precision, recall, F1, ROC-AUC) in API response |

### Alternative: environment variable

```bash
export PIXELPROOF_MODEL_PATH="/path/to/image_forensics_model.pth"
```

---

## 7. How It Works Once Weights Are Placed

1. Place `image_forensics_model.pth` in `backend/app/models/`
2. Ensure `torch` and `torchvision` are installed:
   ```bash
   pip install torch torchvision
   ```
3. Restart the FastAPI backend
4. The `MLDetectorService` auto-discovers the `.pth` file at startup
5. The `/api/analyze` endpoint now returns `ml_analysis.available: true` with real predictions
6. The scoring engine can incorporate ML signal (currently 0 points until weight integration is verified)

---

## 8. Notebook Flask API — Ignored

The notebook (Cell 20) generates a standalone Flask `app.py`. This is **NOT used** by PixelProof.
PixelProof uses FastAPI (`backend/app/main.py`). Only the model architecture, preprocessing,
and inference logic were extracted and integrated into our existing `ml_detector.py`.

---

## 9. Disclaimer

The ML model output is a **probabilistic estimate**, not a definitive verdict.
The `confidence` field represents the model's softmax probability for the predicted class —
it is **NOT** the probability that the entire image is fake.
