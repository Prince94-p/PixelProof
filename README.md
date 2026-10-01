# PixelProof — Digital Image Forensics & Explainable Authenticity Verification

> **"Don't trust the image. Verify the evidence."**

PixelProof is an explainable digital image forensics and manipulation detection platform built for **Problem Statement #22: Image Authenticity Checker**. Unlike opaque "AI detectors" that output unverified black-box percentages ("87% Fake") without evidentiary justification, PixelProof combines five classical, mathematical, and cryptographic forensic modules with an independent deep learning classification signal and Gradient-weighted Class Activation Mapping (Grad-CAM) explainability.

---

## Non-Negotiable Forensic Principles

- **"The 0–100 score is an evidence-weighted forensic suspicion score, not a probability that an image is fake."**
- **"The current weights are initial engineering weights and have not yet been empirically calibrated against a large labelled forensic benchmark."**
- **"The EfficientNet-B0 model is a supporting experimental signal."**
- **"The current ML model detects CASIA-style image manipulation patterns, not AI-generated imagery."**
- **"Evidence quality reflects how much usable forensic information was available for analysis (pixel volume, metadata availability, corroboration). It does not represent the probability that the result is correct."**

---

## Core Architecture & Verification Pipeline

PixelProof operates a multi-engine pipeline ensuring high-throughput security and explainable evidence generation:

```
                          IMAGE UPLOAD
                                ↓
        CHUNKED STREAMING (Early 25MB HTTP 413 Guard)
                                ↓
  DECOMPRESSION BOMB & DIMENSION VALIDATION (50 MP Safe Ceiling)
                                ↓
    BOUNDED ANALYSIS REPRESENTATION (Max 2048px for Vision Tasks)
                                ↓
┌──────────────────────────────────────────────────────────────┐
│                  CLASSICAL FORENSIC ENGINES                  │
├──────────────────────────────────────────────────────────────┤
│ 1. File Integrity & SHA-256 (Exact) + 64-bit DCT pHash       │
│ 2. Metadata / EXIF Inspection (Chronological consistency)    │
│ 3. Error Level Analysis (ELA) (JPEG Q=75..95 sweep + caveats)│
│ 4. Copy-Move Detection (ORB + KNN + RANSAC affine geometry)  │
│ 5. Local Sensor Noise Consistency (MAD residual heatmap)     │
└──────────────────────────────────────────────────────────────┘
                                ↓
        SYNTHESIS & EVIDENCE-WEIGHTED SCORING (0–100)
                                ↓
┌──────────────────────────────────────────────────────────────┐
│             INDEPENDENT DEEP LEARNING SIGNAL                 │
├──────────────────────────────────────────────────────────────┤
│ EfficientNet-B0 (CASIA 2.0 held-out test: 69.62% Acc, 76.36% │
│ ROC-AUC) + Grad-CAM Feature Attribution (score_added = 0)     │
└──────────────────────────────────────────────────────────────┘
                                ↓
         DISAGREEMENT CHECK & EXPLAINABLE FORENSIC REPORT
```

---

## Forensic Modules & Weight Allocations

The Forensic Suspicion Score ranges from **0 to 100** based on **initial heuristic engineering evidence weights**:

| Forensic Module | Max Score | Analytical Technique | Audit Hardening & Key Capabilities |
| :--- | :---: | :--- | :--- |
| **Metadata & EXIF** | 15 | Header parsing, tag analysis, editor signatures | Uses standard `getexif()`, checks chronological timestamp consistency (`DateTime`, `DateTimeOriginal`, `DateTimeDigitized`), flags future or inverted timestamps without treating post-capture saves as fraud. Missing EXIF remains neutral. |
| **Error Level Analysis (ELA)** | 30 | Standardized DCT recompression error | Evaluates JPEG quality sweep ($Q \in [75, 85, 90, 95]$), inspects source quantization tables. Returns `reliability: "limited"` with explanatory caveats for non-JPEG formats (PNG, WebP). |
| **Copy-Move Forgery** | 30 | ORB descriptors, KNN matching, spatial clustering | Features OpenCV RANSAC affine partial geometric modeling (`cv2.estimateAffinePartial2D`) to detect rotated and scaled duplicates while preserving periodic texture suppression for grids, bricks, and foliage. |
| **Noise Consistency** | 20 | High-pass filter, block-level MAD | Normalized against an absolute sensor noise floor rather than per-image dynamic scaling to prevent natural micro-variations from triggering false alarms. |
| **File Integrity** | 5 | Cryptographic hashing & container markers | Calculates SHA-256 for exact byte-level identity, 64-bit DCT perceptual hash (pHash) for visual similarity, and verifies container boundary markers (SOI/EOI/IEND). |
| **Total Classical Score**| **100** | **Initial Evidence Suspicion Score** | **Strictly composed of the 5 classical forensic modules.** |

### Status Classification Thresholds:
- **0–29: Low Suspicion** — Visual and container indicators exhibit uniform consistency with no strong manipulation traces.
- **30–59: Review Recommended** — Moderate anomalies warrant closer manual inspection.
- **60–100: Strong Manipulation Indicators** — Multiple independent modules corroborate localized tampering.

---

## Independent Machine Learning Signal & Explainability

PixelProof includes an optional deep learning classifier based on **EfficientNet-B0** fine-tuned on the CASIA 2.0 dataset:

- **Held-out CASIA 2.0 Generalization (1,893 images):**
  - Accuracy: 69.62%
  - Precision: 59.42%
  - Recall: 79.58%
  - F1 Score: 68.04%
  - ROC-AUC: 76.36%
- **Strict Independence:** The model output is strictly an independent signal (`score_added = 0`) and is never added to the classical 0–100 score.
- **Explainability (Grad-CAM):** Gradient-weighted Class Activation Mapping computes an **ML Influence Map** on the final convolutional feature layer (`model.features[-1]`). This map illustrates regions that influenced the model's classification without claiming to identify confirmed manipulated pixels.
- **Evidence Disagreement Detection:** When classical forensics and ML signals diverge (e.g. low classical score with manipulated-leaning ML signal), PixelProof highlights an Evidence Disagreement notice recommending manual review.

---

## Security & Resource Protection (P0 Hardening)

1. **Chunked Streaming Uploads (Early HTTP 413):** Uploads are processed in 64 KB chunks with an immediate byte counter. Requests exceeding the 25 MB maximum upload ceiling are aborted immediately before buffering excessive memory.
2. **Decompression Bomb Protection:** Pillow's pixel decompression ceiling is safeguarded (`Image.MAX_IMAGE_PIXELS = 100,000,000`), with an explicit processing ceiling of 50 Megapixels (`MAX_TOTAL_PIXELS = 50,000,000`), preventing memory exhaustion attacks from malicious image structures.
3. **Safe Bounded Analysis Representations:** Original bytes are preserved for cryptographic SHA-256, container integrity, and metadata tag inspection. For CPU-intensive computer vision operations (ORB, ELA, noise maps), a bounded representation is created capping the longest dimension to $\le 2048\text{px}$ without upscaling smaller images.
4. **Non-Blocking ASGI Architecture:** CPU-heavy computer vision pipelines are offloaded to worker threads via `asyncio.to_thread`, keeping FastAPI's ASGI event loop fully responsive.

---

## Technology Stack

- **Frontend**: React 18, Vite, Lucide React, CSS3 Design System (Strict Light Theme).
- **Backend**: Python 3.13, FastAPI, Uvicorn, PyTorch (EfficientNet-B0), Torchvision.
- **Computer Vision & Math**: OpenCV (ORB feature matching, RANSAC affine estimation, DCT pHash), Pillow (safe decode, EXIF tag extraction), NumPy (statistical dispersion, MAD).

---

## Installation & Setup

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Application will run locally at `http://localhost:5173`.

### 3. Automated Validation Test Suites

```bash
cd backend
source venv/bin/activate

# Run all test suites
python3 test_audit_hardening.py
python3 test_controlled_forensics.py
python3 test_forensic_pipeline.py
python3 test_ml_integration.py
```

---

## Known Forensic Limitations

- **Social Media Stripping:** Web platforms and messaging networks strip EXIF metadata and heavily compress images, reducing available forensic evidence density.
- **Periodic Natural Textures:** Highly repetitive textures (fences, brick walls, window grids) can cause keypoint clustering; PixelProof employs spatial dispersion and periodic texture filters to minimize false positives.
- **Format Constraints on ELA:** Lossless formats (PNG, WebP) do not have a prior JPEG compression history; ELA is flagged as `limited` reliability for these formats.
- **Model Scope:** The EfficientNet-B0 model is trained on CASIA 2.0 splicing and copy-move manipulations, not generative AI (GAN/Diffusion) image synthesis.

---

## License

MIT License. Copyright (c) 2026 Prince94-p.
