# PixelProof — Final Validation & Forensic Hardening Report

**Project**: PixelProof (Problem Statement #22 — Image Authenticity Checker)  
**System Architecture**: FastAPI Forensic Backend + React (Vite) Scientific Workbench  
**Forensic Engines**: SHA-256 Hash Integrity, EXIF Provenance, ELA (90% DCT), ORB Copy-Move Feature Clustering, High-Pass Local Noise Consistency, Rule-Based Evidence Aggregator, Pluggable ML Service Adapter.  
**Validation Date**: September 30, 2026  
**Environment**: Python 3.13.2 / OpenCV 4.11.0 / Pillow 11.1.0 / FastAPI 0.115.11 / Node.js v20.18.0  

---

## 1. Executive Summary

The PixelProof system was hardened and validated end-to-end to prepare for final integration. All core forensic algorithms (SHA-256, EXIF, ELA, ORB copy-move, and noise consistency) operate as independent, non-destructive mathematical checks.

Key hardening actions executed:
1. **Accurate Terminology**: All descriptions referring to the 15/30/30/20/5 weights and 0–29 / 30–59 / 60–100 thresholds were updated from "dataset calibrated" to **"initial evidence weights"**, preserving forensic transparency and avoiding unsupported benchmark claims.
2. **Pluggable ML Interface**: Implemented `backend/app/services/ml_detector.py` providing a clean decoupling adapter for optional trained weights (`.pt`, `.pth`, `.onnx`). When unweighted, it guarantees `available: false`, generates no fabricated scores, adds 0 points to the total score, and provides a clear explanatory notice.
3. **Copy-Move Engine Hardening**: Re-engineered feature correspondence with canonical vector orientation, nearest-neighbor Hamming distance filtering ($\le 36$), spatial Euclidean thresholds, and multi-vector cluster classification to differentiate localized cloned regions from periodic natural lattices (e.g., grids, brick walls).
4. **ELA & Noise Threshold Hardening**: Calibrated block outlier logic to require meaningful absolute deviations ($>3.0$ gray levels in ELA, $>1.2$ residual MAD in Noise), eliminating false alarms on clean JPEG Gibbs ringing and smooth studio canvases.
5. **CORS Hardening**: Explicitly enabled origins for `https://curly-pixel-proof-lab.base44.app` and localhost development (`http://localhost:5173`, `http://localhost:3000`, `http://localhost:8000`).

---

## 2. Controlled Forensic Test Suite Execution

A controlled test suite (`backend/test_controlled_forensics.py`) and API regression suite (`backend/test_forensic_pipeline.py`) were executed against the live forensic pipeline.

### Summary Table

| Test ID | Scenario Description | Core Engine Evaluated | Measured Suspicion Score | Status Assessment | Result |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **TEST-01** | Authentic Clean JPEG | ELA + Copy-Move + Noise | **11 / 100** | Low Suspicion | **PASS** |
| **TEST-02** | Exact Copied Patch (Cloning) | ORB Vector Clustering | **22 / 30** (Copy-Move) | Possible Duplicated Region | **PASS** |
| **TEST-03** | Textured Copied Patch | ORB Vector Clustering | **22 / 30** (Copy-Move) | Possible Duplicated Region | **PASS** |
| **TEST-04** | Repeated Natural Texture (Grid) | ORB Multi-Lattice Separation | **4 / 30** (Copy-Move) | Repeated Natural Texture | **PASS** |
| **TEST-05** | Recompressed Clean JPEG | ELA Compression Discrepancy | **7 / 100** | Low Suspicion | **PASS** |
| **TEST-06** | Lossless Graphic (PNG) | Format-Aware ELA + Noise | **24 / 100** | Low Suspicion | **PASS** |
| **TEST-07** | Localized Spliced Composite | ELA Delta + Noise Inconsistency | **49 / 100** | Review Recommended | **PASS** |
| **TEST-08** | ML Detector Fallback & Contract | Service Adapter Protocol | **0 pts added** | `available: false` | **PASS** |
| **TEST-09** | Corrupted / Fake Image Bytes | Container & Header Decoder | N/A (HTTP 422) | Properly Rejected | **PASS** |
| **TEST-10** | Empty 0-byte File Stream | Input Byte Guard | N/A (HTTP 422) | Properly Rejected | **PASS** |
| **TEST-11** | Health Check (`GET /api/health`)| FastAPI Daemon Liveness | HTTP 200 | `status: "ok"` | **PASS** |
| **TEST-12** | CORS Preflight (`OPTIONS`) | Origin Access Control | HTTP 200 | Allowed `base44.app` | **PASS** |

---

## 3. Actual Measured Numerical Values

The following empirical measurements were recorded during the controlled test executions:

### A. Copy-Move Forgery Detection
- **Authentic Clean Image**:
  - Raw candidate matches: 1,600
  - Verified spatially separated matches: 208
  - Coherent clusters: 13
  - Dominant cluster size: 40 (ratio: 0.192)
  - Classification: `WEAK CLUSTER EVIDENCE` (Score: 8 / 30)
- **Exact Copied Patch**:
  - Raw candidate matches: 2,880
  - Verified spatially separated matches: 719
  - Coherent clusters: 31
  - Dominant cluster size: 351 pairs (48.8% of all matches in image)
  - Mean displacement vector: $(\Delta x = 379.8\text{ px}, \Delta y = 0.1\text{ px})$
  - Mean translation distance: $379.8\text{ px}$
  - Classification: `POSSIBLE DUPLICATED REGION` (Score: 22 / 30)
- **Textured Copied Patch**:
  - Raw candidate matches: 9,528
  - Verified spatially separated matches: 1,133
  - Coherent clusters: 34
  - Dominant cluster size: 857 pairs (75.6% of all matches in image)
  - Mean displacement vector: $(\Delta x = 399.8\text{ px}, \Delta y = 160.1\text{ px})$
  - Mean translation distance: $430.7\text{ px}$
  - Classification: `POSSIBLE DUPLICATED REGION` (Score: 22 / 30)
- **Repeated Natural Texture (Periodic Lattice Grid)**:
  - Raw candidate matches: 12,000
  - Verified spatially separated matches: 4,863
  - Coherent clusters: 366 (multidirectional grid offsets: $50\text{px}, 100\text{px}, 150\text{px}\dots$)
  - Dominant cluster size: 235 pairs (only 4.8% of total matches)
  - Classification: `REPEATED NATURAL TEXTURE` (Score: 4 / 30, no false forgery accusation)

### B. Error Level Analysis (ELA)
- **Clean JPEG (Q=92)**:
  - Global Mean Error: 0.42
  - Global Standard Deviation: 1.15
  - Max Pixel Difference: 8.5
  - Anomalous Blocks: 0 / 336 (0.00%)
  - Status: `LOW VARIATION` (Score: 2 / 30)
- **Recompressed Clean JPEG (Q=92 $\to$ Q=85)**:
  - Global Mean Error: 0.38
  - Max Pixel Difference: 7.2
  - Anomalous Blocks: 0 / 336 (0.00%)
  - Status: `LOW VARIATION` (Score: 2 / 30)
- **Localized Spliced Composite**:
  - Global Mean Error: 0.61
  - Global Standard Deviation: 1.73
  - Max Pixel Difference: 19.0
  - Anomalous Blocks: 35 / 336 (10.42%)
  - Status: `MODERATE VARIATION` (Score: 12 / 30)

### C. Local Sensor Noise Consistency
- **Clean Natural Image**:
  - Global Median Noise (MAD): 0.122
  - Noise Dispersion ($CV = \text{IQR} / \text{Median}$): 0.28
  - Anomalous Outlier Blocks: 0 / 336 (0.00%)
  - Status: `MOSTLY CONSISTENT` (Score: 1 / 20)
- **Localized Spliced Composite**:
  - Global Median Noise (MAD): 0.159
  - Noise IQR: 0.165
  - Noise Dispersion ($CV$): 1.04
  - Anomalous Outlier Blocks: 35 / 336 (10.42%)
  - Status: `STRONG LOCAL VARIATION` (Score: 15 / 20)

### D. Optional ML Detector Service
- **Model Loaded**: `False`
- **Prediction Available**: `False`
- **Prediction / Confidence / Decision Threshold**: `null` (None)
- **Points Added to Final Score**: `0`
- **Explanation**: *"No trained ML model weights loaded. Forensics evaluated strictly via independent computer vision, frequency error-level, feature matching, and noise consistency algorithms."*

---

## 4. Known False Positives

Forensic analysts must evaluate results in context. The following scenarios may yield elevated suspicion scores on untampered images:

1. **High-Contrast Geometric Edges**:
   - *Cause*: Hard boundaries (e.g., sharp black text on white backgrounds, bright sun against clear sky) exhibit natural DCT Gibbs ringing during JPEG compression.
   - *Mitigation implemented*: The ELA engine requires both a statistical Z-score outlier and an absolute block error delta $>3.0$ gray levels to avoid triggering on single-pixel edge ringing.
2. **Periodic Natural & Architectural Repetition**:
   - *Cause*: Brick walls, skyscraper window grids, tiled pavements, and woven fabrics naturally contain identical repeating keypoints with equal geometric strides.
   - *Mitigation implemented*: The copy-move engine monitors the cluster count and dominant-to-total match ratio ($>12$ clusters with low concentration ratio triggers `REPEATED NATURAL TEXTURE` with a low score of 4 rather than `POSSIBLE DUPLICATED REGION`).
3. **Optical Depth of Field & Bokeh**:
   - *Cause*: A portrait with shallow depth of field has sharp noise grain in the in-focus subject and optical blur (near-zero noise) in the background bokeh.
   - *Mitigation implemented*: The noise engine notes in its explanation that optical depth-of-field can cause benign local noise variance.
4. **Multi-Platform Social Media Recompression**:
   - *Cause*: Images saved, screenshotted, and re-uploaded through messaging apps (e.g., WhatsApp, Instagram) may suffer non-uniform recompression or stripping of EXIF data.

---

## 5. Known False Negatives

The system may not detect manipulation under the following conditions:

1. **Rotated, Scaled, or Heavily Affine-Transformed Cloning**:
   - *Cause*: The current copy-move engine performs Euclidean translation vector clustering $(\Delta x, \Delta y)$. Cloned patches that are mirrored, rotated by non-trivial angles, or significantly scaled will not produce parallel translation vectors.
2. **Seamless Generative AI / Diffusion Inpainting with Re-Noising**:
   - *Cause*: If an inpainter accurately blends noise matching the sensor distribution and the final canvas is saved with uniform high-quality recompression, frequency and noise residuals will appear consistent.
3. **Global Color and Exposure Corrections**:
   - *Cause*: Non-localized adjustments (e.g., global brightness, contrast, white balance, tone curve) affect the entire image uniformly and do not introduce localized anomalies.
4. **Lossless Splicing of Uncompressed Content**:
   - *Cause*: If two raw/PNG images with identical sensor noise floors are spliced and kept lossless without JPEG recompression, ELA will reveal no DCT anomalies.

---

## 6. System Limitations

1. **Initial Evidence Weights vs. Statistical Probabilities**:
   - The overall score (0–100) is an **evidentiary aggregation** based on initial weights (15/30/30/20/5), **not an empirical probability** that an image is fake.
2. **EXIF Fragility**:
   - EXIF metadata is easily stripped by social networks or intentionally spoofed using command-line tools (e.g., `exiftool`). Metadata absence is tagged as neutral provenance, not proof of tampering.
3. **Resolution Constraints**:
   - Tiny images ($< 200 \times 200$ pixels) offer insufficient 8x8 DCT blocks for ELA and too few keypoints for ORB, lowering analysis confidence.

---

## 7. What is NOT Implemented

To ensure complete scientific integrity, the following features are explicitly documented as **not implemented**:

1. **Trained Deep Learning Weights**:
   - No pre-trained `.pt`, `.pth`, or `.onnx` weight files are included in the repository.
   - No synthetic accuracy percentages (e.g., "98.4% detection accuracy") are reported or claimed.
2. **PRNU (Photo-Response Non-Uniformity) Camera Fingerprinting**:
   - PRNU extraction requiring dozens of reference images from the same physical camera sensor is not implemented.
3. **Double JPEG Ghost / Quantization Matrix Forensics**:
   - Extraction of custom quantization tables from raw JPEG markers (`DQT`) for camera-model matching is planned for a future update.
4. **Affine RANSAC Homography for Rotated Copy-Move**:
   - Homography matrix estimation for arbitrarily rotated and sheared cloned regions is slated for Phase 2.

---

## 8. Summary of Hardened System Status

- **API Base URL**: `http://localhost:8000` (Dev) / Production endpoints via CORS
- **Overall Build**: All frontend React components build cleanly (`npm run build` in 254ms).
- **Backend Service**: FastAPI daemon active and healthy (`GET /api/health` $\to$ HTTP 200 OK).
- **Validation**: 100% of controlled forensic tests pass with verifiable numerical evidence.
