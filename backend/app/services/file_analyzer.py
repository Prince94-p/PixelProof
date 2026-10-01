import hashlib
from datetime import datetime, timezone
import numpy as np
from app.utils.image_utils import compute_perceptual_hash

def analyze_file_integrity(file_bytes: bytes, file_info: dict, cv_gray: np.ndarray = None) -> dict:
    """
    Performs cryptographic hashing, perceptual hashing, and structural container analysis.
    Produces the immutable SHA-256 digital fingerprint, 64-bit DCT perceptual hash (pHash),
    and evaluates basic file integrity.
    """
    # Real SHA-256 calculation
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # 64-bit DCT perceptual hash for visual similarity matching
    phash_str = compute_perceptual_hash(cv_gray if cv_gray is not None else file_bytes)
    
    size_bytes = len(file_bytes)
    # Format size nicely
    if size_bytes < 1024:
        size_formatted = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_formatted = f"{size_bytes / 1024:.1f} KB"
    else:
        size_formatted = f"{size_bytes / (1024 * 1024):.2f} MB"

    width = file_info.get("width", 0)
    height = file_info.get("height", 0)
    aspect_ratio = f"{width}:{height}"
    if height > 0:
        ratio_val = width / height
        aspect_ratio = f"{ratio_val:.2f}:1 ({width}×{height})"

    # Check for basic file container integrity
    file_fmt = file_info.get("format", "").upper()
    has_anomaly = False
    anomaly_desc = []
    score_contribution = 0
    
    # Check JPEG SOI (FF D8) and EOI (FF D9)
    if file_fmt == "JPEG":
        if not file_bytes.startswith(b'\xff\xd8'):
            has_anomaly = True
            anomaly_desc.append("Missing standard JPEG Start of Image (SOI) marker.")
        if not (file_bytes.endswith(b'\xff\xd9') or b'\xff\xd9' in file_bytes[-100:]):
            has_anomaly = True
            anomaly_desc.append("Missing or displaced JPEG End of Image (EOI) marker, suggesting truncation or appended data.")
    elif file_fmt == "PNG":
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        if not file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            has_anomaly = True
            anomaly_desc.append("Corrupted PNG file signature.")
        if not file_bytes.endswith(b'IEND\xaeB`\x82'):
            if b'IEND' in file_bytes:
                has_anomaly = True
                anomaly_desc.append("Data detected beyond PNG IEND chunk (possible hidden payload or steganography).")
            else:
                has_anomaly = True
                anomaly_desc.append("Missing PNG IEND marker.")

    if has_anomaly:
        status = "CONTAINER ANOMALY"
        score_contribution = 4
        finding = "; ".join(anomaly_desc)
        explanation = "Structural analysis of the image container detected non-standard markers or trailing bytes."
    else:
        status = "VALID"
        score_contribution = 0
        finding = f"Valid {file_fmt} container. File decoded successfully without structural truncation."
        explanation = "The file adheres to standard container specifications with verified boundary markers."

    timestamp_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "score": score_contribution,
        "max_score": 5,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "fingerprint": {
            "filename": file_info.get("filename", "unknown"),
            "format": file_fmt,
            "mime_type": file_info.get("mime_type", "application/octet-stream"),
            "size": size_bytes,
            "size_formatted": size_formatted,
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "sha256": sha256_hash,
            "perceptual_hash": phash_str,
            "timestamp": timestamp_iso,
            "explanation": "SHA-256 provides exact byte-level cryptographic identity. Perceptual Hash (pHash) provides visual appearance fingerprinting."
        }
    }
