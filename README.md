# PixelProof — Digital Image Forensics & Authenticity Verification

> **"Don't trust the image. Verify the evidence."**

PixelProof is a full-stack digital image forensics platform built to address **Problem Statement #22: Image Authenticity Checker**. Unlike black-box AI detectors that output opaque percentages ("87% Fake") without justification, PixelProof performs multiple independent scientific, mathematical, and cryptographic analyses on the actual image bytes to provide explainable forensic evidence.

---

## Key Features

1. **Cryptographic SHA-256 Digital Fingerprint**: Generates an immutable cryptographic fingerprint from the raw file bytes for provenance tracking and chain-of-custody verification.
2. **EXIF & Container Metadata Forensics**: Inspects hardware acquisition tags (Camera Make/Model), original timestamps, and software signatures (e.g., Adobe Photoshop, GIMP, Lightroom, Canva).
3. **Error Level Analysis (ELA)**: Recompresses image pixels at a standardized 90% JPEG quality level to detect localized recompression anomalies characteristic of spliced or pasted elements.
4. **Copy-Move Forgery Detection**: Employs OpenCV ORB feature extraction, nearest-neighbor matching, spatial separation filters, and displacement vector clustering to identify cloned regions.
5. **Local Sensor Noise Consistency**: Extracts high-frequency residuals using Gaussian blur subtraction and computes local noise dispersion (Median Absolute Deviation) to uncover spliced zones or airbrushed retouching.
6. **Transparent Forensic Suspicion Score (0–100)**: An initial multi-engine evidence weighting system with confidence levels and itemized evidence explanations.
7. **Strict Light Theme UI**: A clean, high-contrast, scientific laboratory design using an enterprise blue/white palette.

---

## Architecture & Forensic Pipeline

```
IMAGE UPLOAD
      ↓
FILE VALIDATION (Format, Dimension, Container Integrity)
      ↓
METADATA / EXIF INSPECTION
      ↓
ERROR LEVEL ANALYSIS (90% DCT Recompression)
      ↓
COPY-MOVE FORGERY DETECTION (ORB + Vector Clustering)
      ↓
NOISE CONSISTENCY ANALYSIS (High-Pass Residual MAD)
      ↓
FILE INTEGRITY + SHA-256 FINGERPRINT
      ↓
EVIDENCE CROSS-CHECKING & SCORING ENGINE
      ↓
INTERACTIVE VISUAL EVIDENCE & EXPLAINABLE REPORT
```

---

## Scoring Weight & Interpretation

The Forensic Suspicion Score ranges from **0 to 100** using **initial evidence weights**:

| Forensic Module | Max Score | Description |
| :--- | :---: | :--- |
| **Metadata & Software** | 15 | Detects editing software traces and tag incongruities. |
| **Error Level Analysis (ELA)** | 30 | Measures localized DCT recompression discrepancies. |
| **Copy-Move Detection** | 30 | Clusters coherent translation vectors between matched features. |
| **Noise Consistency** | 20 | Evaluates local sensor noise floor deviation across blocks. |
| **File Integrity** | 5 | Verifies standard container markers (SOI/EOI/IEND). |
| **Total** | **100** | **Initial Evidence Suspicion Score** |

### Suspicion Ranges:
- **0–29: Low Suspicion** — Findings are consistent across all independent engines.
- **30–59: Review Recommended** — Moderate anomalies warrant closer manual inspection.
- **60–100: Strong Manipulation Indicators** — Multiple independent modules corroborate localized tampering.

> **Forensic Principle:** The score represents the strength of detected forensic indicators. It is not the probability that an image is fake.

---

## Technology Stack

- **Frontend**: React 18, Vite, Lucide React, CSS3 Design System (Strict Light Theme).
- **Backend**: Python 3, FastAPI, Uvicorn.
- **Forensic & Computer Vision Engines**: OpenCV (ORB feature detector, spatial matching, morphological hulls), Pillow (EXIF header parsing, DCT compression simulation), NumPy (statistical dispersion, MAD, matrix operations).

---

## Folder Structure

```
pixelproof/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ScoreGauge.jsx
│   │   │   ├── ForensicViewer.jsx
│   │   │   ├── EvidenceCard.jsx
│   │   │   ├── MetadataPanel.jsx
│   │   │   ├── DigitalFingerprint.jsx
│   │   │   └── LoadingAnalysis.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Analyze.jsx
│   │   │   ├── Results.jsx
│   │   │   └── HowItWorks.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── styles.css
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── analysis.py
│   │   ├── services/
│   │   │   ├── file_analyzer.py
│   │   │   ├── metadata_analyzer.py
│   │   │   ├── ela_analyzer.py
│   │   │   ├── copy_move_detector.py
│   │   │   ├── noise_analyzer.py
│   │   │   └── scoring_engine.py
│   │   └── utils/
│   │       ├── image_utils.py
│   │       └── validators.py
│   └── requirements.txt
└── README.md
```

---

## Installation & Running Locally

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

The backend API will be running at `http://localhost:8000`.  
Health check endpoint: `GET http://localhost:8000/api/health`.

### 2. Frontend Setup

```bash
# Navigate to frontend directory in another terminal
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## API Specification

### `GET /api/health`
Response:
```json
{
  "status": "ok",
  "service": "PixelProof Forensics"
}
```

### `POST /api/analyze`
Accepts `multipart/form-data` with an image file (`JPG`, `JPEG`, `PNG`, or `WEBP`).

Response structure:
```json
{
  "analysis_id": "0fc9b081-3444-4dd2-89da-5a0ec7b2fe5b",
  "file": {
    "filename": "sample.jpg",
    "format": "JPEG",
    "mime_type": "image/jpeg",
    "size": 245120,
    "size_formatted": "239.4 KB",
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "1.78:1 (1920×1080)",
    "sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
    "timestamp": "2026-09-30 20:45:10 UTC"
  },
  "result": {
    "score": 48,
    "max_score": 100,
    "status": "Review Recommended",
    "status_code": "warning",
    "confidence": "Moderate",
    "confidence_description": "Moderate confidence based on standard evidence availability.",
    "summary": "Several forensic indicators warrant closer inspection.",
    "disclaimer": "This score represents the strength of detected forensic indicators. It is not the probability that the image is fake.",
    "breakdown": {
      "metadata": {"score": 8, "max": 15},
      "ela": {"score": 16, "max": 30},
      "copy_move": {"score": 20, "max": 30},
      "noise": {"score": 4, "max": 20},
      "file_integrity": {"score": 0, "max": 5}
    }
  },
  "metadata": { ... },
  "ela": {
    "score": 16,
    "max_score": 30,
    "status": "MODERATE VARIATION",
    "finding": "Localized recompression differences observed.",
    "explanation": "...",
    "visualization": "data:image/png;base64,..."
  },
  "copy_move": { ... },
  "noise": { ... },
  "file_integrity": { ... },
  "evidence": [ ... ],
  "original_preview": "data:image/jpeg;base64,..."
}
```

---

## Limitations of Digital Image Forensics

- **Social Media Compression**: Messaging apps and social networks routinely re-encode and strip metadata from images.
- **Repetitive Textures**: Natural architectural windows or foliage grids can produce false-positive keypoint matches.
- **Absence of EXIF**: Missing metadata is standard web behavior and is never treated as standalone proof of manipulation.
- **Optical Depth-of-Field (Bokeh)**: Shallow depth of field yields smooth, low-noise backgrounds naturally.

---

## License

MIT License. Developed for Problem Statement #22 — Image Authenticity Checker.
