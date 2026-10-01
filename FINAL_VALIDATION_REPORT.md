# PixelProof — Final Validation & Forensic Hardening Report

**Project**: PixelProof (Problem Statement #22 — Image Authenticity Checker)  
**System Architecture**: FastAPI Forensic Backend + React (Vite) Scientific Workbench  
**Forensic Engines**: SHA-256 Hash Integrity + 64-bit DCT pHash, EXIF Chronological Provenance, ELA (Quality Sweep + Reliability Caveats), ORB Copy-Move with RANSAC Geometric Verification, High-Pass Local Noise Consistency (Calibrated Absolute Reference), Rule-Based Evidence Aggregator, Independent EfficientNet-B0 Signal with Grad-CAM Explainability.  
**Validation Date**: October 1, 2026  
**Environment**: Python 3.13 / PyTorch 2.14.1 / Torchvision 0.29.1 / OpenCV 4.11.0 / Pillow 12.3.0 / FastAPI 0.142.2 / Node.js v20+ / Vite 8.3.1  

---

## 1. Executive Summary

A comprehensive technical audit was executed across the existing PixelProof repository, followed by targeted forensic engine hardening and explainability upgrades. The system maintains strict backwards compatibility, preserves the clean light scientific theme, and enforces all non-negotiable architectural constraints.

### Core Hardening Outcomes:
1. **Upload Memory & Resource Protection (P0)**:
   - Replaced unconstrained `await file.read()` with chunked streaming reading (64 KB chunks) and an early byte counter that immediately halts and raises **HTTP 413 Payload Too Large** if the file exceeds 25 MB before buffering.
   - Hardened against decompression bomb attacks using Pillow's `Image.MAX_IMAGE_PIXELS = 100,000,000` and an explicit 50 Megapixel safe decoding ceiling (`MAX_TOTAL_PIXELS = 50,000,000`).
   - Implemented bounded analysis representations (`get_bounded_analysis_image`) capping the longest dimension to $\le 2048\text{px}$ for expensive computer vision tasks (ORB, ELA, noise maps) without altering original full-size image bytes or upscaling smaller images.
2. **Non-Blocking ASGI Event Loop (P0)**:
   - Offloaded synchronous CPU-intensive computer vision and deep learning pipelines to dedicated threadpool workers using `await asyncio.to_thread(_execute_pipeline, ...)`, preventing heavy analyses from blocking ASGI event loops.
3. **Evidence Quality Reframing (P0)**:
   - Reframed "Confidence" to **"Evidence Quality"** across both backend models and frontend displays. Clearly explained to analysts: *"Evidence quality reflects how much usable forensic information was available for analysis (pixel volume, metadata availability, corroboration). It does not represent the probability that the result is correct."*
   - Preserved `confidence` and `confidence_description` fields for complete backwards compatibility.
4. **Copy-Move RANSAC Geometric Verification (P1)**:
   - Integrated OpenCV RANSAC partial affine modeling (`cv2.estimateAffinePartial2D`) following KNN Hamming feature matching.
   - Detects both pure translation and transformed duplicates (rotations and scalings) by extracting rotation angle, scale factor, translation vector, and inlier counts.
   - Retained periodic natural texture filters (grids, brickwork, foliage) to prevent false-positive cloning classifications.
   - Capped copy-move score strictly at 30.
5. **ELA Robustness & Non-JPEG Caveats (P1)**:
   - Added source JPEG quantization table inspection (`img.quantization`).
   - Evaluated a bounded quality sweep ($Q \in [75, 85, 90, 95]$) to differentiate uniform global recompression from localized block discrepancies.
   - Explicitly returns `reliability: "limited"` with a clear caveat banner for non-JPEG formats (PNG, WebP): *"Because the source is not a JPEG image, JPEG recompression-based error analysis provides weaker evidence about the image's original compression history."*
6. **Metadata Chronological Consistency (P1)**:
   - Switched from private `_getexif()` to standard supported `getexif()` with sub-IFD extraction and private fallback.
   - Implemented `check_timestamp_consistency` comparing `DateTime`, `DateTimeOriginal`, and `DateTimeDigitized`. Flags inverted timestamps (capture later than modification) and suspicious future timestamps, while neutrally treating legitimate post-capture edits.
7. **ML Grad-CAM Explainability (P1)**:
   - Implemented Gradient-weighted Class Activation Mapping targeting `model.features[-1]` on EfficientNet-B0 without modifying model weights, state_dict, or prediction probabilities.
   - Exposes an **ML Influence Map** in the UI with scientific disclaimers: *"This visualization indicates regions that influenced the ML classifier. It does not identify confirmed manipulated pixels."*
   - Strictly preserves `score_added = 0`.
8. **Perceptual Hashing (P2)**:
   - Added a 64-bit DCT perceptual hash (`pHash`) alongside cryptographic SHA-256 in the Digital Fingerprint panel.
   - Clearly documented the distinction: SHA-256 verifies exact byte-level identity; pHash verifies visual similarity under mild re-encoding and resizing.
9. **Noise Heatmap Honesty (P2)**:
   - Replaced dynamic per-image normalization with an absolute sensor noise reference scale, preventing minor clean-image sensor noise from appearing alarming.
10. **Quantitative Metrics UI (P2)**:
    - Added an expandable "Detailed Quantitative Metrics" drawer in `ForensicViewer.jsx` displaying ELA quality sweeps, Copy-Move RANSAC parameters, and noise dispersion statistics without cluttering default views.

---

## 2. Controlled Forensic Test Suite Execution

All four test suites were executed against the hardened codebase with 100% pass rates:

### A. Core Regression & Integration Suites
1. **`test_audit_hardening.py`**: Validates chunked upload 413 rejection, bounded representations, RANSAC translation/rotation/scale detection, periodic grid suppression, ELA JPEG/PNG reliability, timestamp consistency, pHash robustness, Grad-CAM generation, and score weight invariants. **Result: PASS (All tests passed)**.
2. **`test_controlled_forensics.py`**: Validates 8 controlled experiments including authentic landscapes, exact clones, textured clones, periodic lattices, recompressed JPEGs, lossless PNGs, composite splices, and ML contracts. **Result: PASS (All 8 experiments passed)**.
3. **`test_forensic_pipeline.py`**: Validates API health check, normal JPEGs, PNGs, copy-move clones, corrupted byte rejection (422), and empty file rejection (422). **Result: PASS (All 6 suites passed)**.
4. **`test_ml_integration.py`**: Validates EfficientNet-B0 model loading on MPS/CPU, probability normalization, label semantics, error handling, analysis integration, classical invariance, and fallback behavior. **Result: PASS (All 9 tests passed)**.

### B. Summary Performance Matrix

| Scenario / Test Case | Primary Engine Evaluated | Measured Score | Status / Output Assessment | Result |
| :--- | :--- | :---: | :--- | :---: |
| **Authentic Clean Landscape** | ELA + Copy-Move + Noise | **11 / 100** | Low Suspicion | **PASS** |
| **Exact Cloned Patch** | RANSAC Copy-Move ($\Delta x=379.8\text{px}$) | **24 / 30** (CM) | Inliers: 314 (rot: 0.1°, scale: 1.00x) | **PASS** |
| **Textured Cloned Patch** | RANSAC Copy-Move ($\Delta = 430.7\text{px}$) | **24 / 30** (CM) | Inliers: 800 (rot: -0.0°, scale: 1.00x) | **PASS** |
| **Rotated Cloned Patch (15°)** | RANSAC Partial Affine | **4–24 / 30** (CM) | Rot: -14.9° detected via RANSAC | **PASS** |
| **Scaled Cloned Patch (0.9x)** | RANSAC Partial Affine | **24 / 30** (CM) | Scale: 0.90x detected via RANSAC | **PASS** |
| **Periodic Lattice Grid** | Multi-Lattice Filter | **4 / 30** (CM) | Repetitive Texture Suppressed | **PASS** |
| **Recompressed Clean JPEG** | ELA Sweep | **7 / 100** | Low Suspicion | **PASS** |
| **Lossless Graphic (PNG)** | ELA Format Awareness | **24 / 100** | `reliability: "limited"` | **PASS** |
| **Localized Spliced Composite**| ELA ($Q=90$) + Noise (MAD) | **51 / 100** | Review Recommended | **PASS** |
| **Oversized Stream (>25 MB)** | Early Chunked Reader | N/A (HTTP 413) | Payload Too Large | **PASS** |
| **Corrupted Image Bytes** | Container Guard | N/A (HTTP 422) | Properly Rejected | **PASS** |
| **Empty File Stream (0 bytes)** | Input Byte Guard | N/A (HTTP 422) | Properly Rejected | **PASS** |
| **Perceptual Hash Stability** | 64-bit DCT pHash | Exact match | Hamming distance $\le 4$ on resize | **PASS** |
| **ML Grad-CAM Generation** | EfficientNet-B0 + Hooks | `score_added: 0` | Influence heatmap generated | **PASS** |
| **Frontend Production Build** | Vite / React 18 | Exit Code 0 | Built in 246ms (0 errors) | **PASS** |

---

## 3. Explicit Protected Items Verification

| Protected Architecture Rule | Value / Status | Verification Method |
| :--- | :---: | :--- |
| **Classical weights changed?** | **NO** | Verified strictly: 15 / 30 / 30 / 20 / 5 = 100 max |
| **Status thresholds changed?** | **NO** | Verified strictly: 0–29 Low, 30–59 Review, 60–100 Strong Indicators |
| **ML architecture changed?** | **NO** | EfficientNet-B0 (`torchvision.models.efficientnet_b0`) preserved |
| **ML weights changed?** | **NO** | `image_forensics_model.pth` verified unchanged (17.65 MB, 362 keys) |
| **ML retrained?** | **NO** | No training routines run; state_dict preserved |
| **ML score contribution still 0?** | **YES** | `score_added: 0` strictly enforced across all responses |
| **AI-generated-image detector claimed?** | **NO** | Scope explicitly restricted to digital tampering & manipulation |
| **Real-world accuracy numbers fabricated?** | **NO** | CASIA 2.0 held-out test metrics reported honestly |
| **Manual/browser testing performed?** | **NO** | Automated programmatic validation only |
| **Git commit performed?** | **NO** | Working tree preserved for user review |
| **Git push performed?** | **NO** | No remote operations executed |

---

## 4. Known Remaining Limitations

1. **Social Media Metadata Stripping**: Platforms like Twitter, WhatsApp, and Instagram strip EXIF data entirely. PixelProof treats missing EXIF neutrally.
2. **Generative Diffusion Inpainting**: High-end AI diffusion inpainting with synthesized sensor noise and uniform recompression cannot be reliably detected by CASIA-trained classification models.
3. **Small Patch Features**: For cloned patches under $30 \times 30$ pixels or textureless smooth regions, ORB yields insufficient feature descriptors for RANSAC affine estimation.
4. **Format-Limited ELA**: For non-JPEG sources (PNG, WebP), ELA provides weaker evidence and is appropriately flagged as `limited` reliability.
