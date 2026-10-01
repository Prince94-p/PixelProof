import io
import numpy as np
from PIL import Image
import cv2
from app.utils.image_utils import encode_cv2_to_base64_data_uri

def analyze_ela(rgb_img: Image.Image, cv_bgr: np.ndarray, file_format: str) -> dict:
    """
    Performs real Error Level Analysis (ELA) by recompressing the image
    at a known quality level (90%) and analyzing localized recompression discrepancies.
    """
    h, w = cv_bgr.shape[:2]
    max_score = 30
    
    # Step 1: Recompress internally as JPEG at quality 90
    buffer = io.BytesIO()
    rgb_img.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)
    
    # Step 2: Reload recompressed image
    recompressed_pil = Image.open(buffer)
    recompressed_rgb = np.array(recompressed_pil)
    recompressed_bgr = cv2.cvtColor(recompressed_rgb, cv2.COLOR_RGB2BGR)
    
    # Step 3: Compute pixel-wise absolute difference
    diff = cv2.absdiff(cv_bgr, recompressed_bgr).astype(np.float32)
    
    # Step 4: Convert difference to grayscale for statistical analysis
    gray_diff = cv2.cvtColor(diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    
    # Global metrics
    global_mean = float(np.mean(gray_diff))
    global_std = float(np.std(gray_diff))
    max_diff = float(np.max(gray_diff))
    
    # Step 5: Adaptive scaling for visual display
    # Scale differences so human eyes can clearly inspect compression levels
    scale_factor = 12.0
    if max_diff > 0:
        # Prevent extreme blow-out while amplifying subtle recompression traces
        scale_factor = min(20.0, max(8.0, 220.0 / max(max_diff, 1.0)))
    
    visual_ela = np.clip(diff * scale_factor, 0, 255).astype(np.uint8)
    
    # Step 6: Block-based localized anomaly analysis
    # High-contrast edges naturally show higher DCT recompression error.
    # We detect local patches that strongly deviate from surrounding context.
    block_size = max(16, min(48, min(h, w) // 16))
    blocks_y = h // block_size
    blocks_x = w // block_size
    
    anomalous_blocks = 0
    total_blocks = max(1, blocks_y * blocks_x)
    block_means = []
    
    for by in range(blocks_y):
        for bx in range(blocks_x):
            y1 = by * block_size
            y2 = y1 + block_size
            x1 = bx * block_size
            x2 = x1 + block_size
            
            block_gray = gray_diff[y1:y2, x1:x2]
            b_mean = np.mean(block_gray)
            block_means.append(b_mean)
            
    block_means = np.array(block_means)
    bm_mean = float(np.mean(block_means))
    bm_std = float(np.std(block_means))
    
    if bm_std > 0.4:
        # Require both statistical outlier (Z-score > 2.4) AND meaningful absolute error delta (> 3.0)
        abs_diffs = block_means - bm_mean
        z_scores = abs_diffs / bm_std
        anomalous_blocks = int(np.sum((z_scores > 2.4) & (abs_diffs > 3.0)))
        anomaly_ratio = anomalous_blocks / total_blocks
    else:
        anomalous_blocks = 0
        anomaly_ratio = 0.0

    # Format-aware adjustments
    is_jpeg = file_format.upper() in ("JPEG", "JPG")
    
    # Step 7: Bounded Quality Sweep & Quantization Inspection
    source_compression = {
        "has_quantization_tables": False,
        "evidence": "No direct quantization tables detected."
    }
    
    if hasattr(rgb_img, "quantization") and rgb_img.quantization:
        try:
            q_tables = rgb_img.quantization
            t0 = q_tables[0] if isinstance(q_tables, dict) and 0 in q_tables else (q_tables[0] if isinstance(q_tables, (list, tuple)) else None)
            if t0 is not None:
                t0_vals = list(t0.values()) if isinstance(t0, dict) else list(t0)
                avg_luma = float(np.mean(t0_vals))
                source_compression = {
                    "has_quantization_tables": True,
                    "quantization_tables_count": len(q_tables),
                    "luminance_table_average": round(avg_luma, 1),
                    "evidence": "Source JPEG quantization tables extracted for baseline recompression context."
                }
        except Exception:
            pass

    # Small bounded quality sweep: [75, 85, 90, 95]
    quality_tests = []
    for test_q in (75, 85, 90, 95):
        if test_q == 90:
            quality_tests.append({
                "quality": 90,
                "mean_error": round(global_mean, 2),
                "max_diff": round(max_diff, 1)
            })
        else:
            try:
                buf_q = io.BytesIO()
                rgb_img.save(buf_q, format="JPEG", quality=test_q)
                buf_q.seek(0)
                recomp_q = np.array(Image.open(buf_q))
                recomp_bgr_q = cv2.cvtColor(recomp_q, cv2.COLOR_RGB2BGR)
                diff_q = cv2.absdiff(cv_bgr, recomp_bgr_q)
                gray_q = cv2.cvtColor(diff_q, cv2.COLOR_BGR2GRAY)
                quality_tests.append({
                    "quality": test_q,
                    "mean_error": round(float(np.mean(gray_q)), 2),
                    "max_diff": round(float(np.max(gray_q)), 1)
                })
            except Exception:
                pass

    reliability = "standard" if is_jpeg else "limited"
    reliability_note = (
        "Standard JPEG DCT recompression error analysis evaluated across quantization tables."
        if is_jpeg else
        "Because the source is not a JPEG image, JPEG recompression-based error analysis provides weaker evidence about the image's original compression history."
    )

    # Step 8: Initial Evidence Weight & Classification
    # To prevent false positives on natural sharp edges or uniform recompression:
    # Require both statistical outlier blocks AND elevated peak recompression delta
    if anomaly_ratio > 0.07 and max_diff > 16.0 and bm_std > 1.5:
        status = "STRONG LOCAL VARIATION"
        score = 22 if is_jpeg else 16
        finding = f"Significant localized error-level disparities detected across {anomalous_blocks} image blocks."
        explanation = (
            "Discrepancies in JPEG recompression error suggest regions with differing compression histories. "
            "Pasted or digitally modified elements often exhibit sharper or duller recompression signatures than the background."
        )
    elif (anomaly_ratio > 0.035 and max_diff > 13.0) or (anomaly_ratio > 0.05 and bm_std > 1.1):
        status = "MODERATE VARIATION"
        score = 12 if is_jpeg else 8
        finding = f"Moderate recompression variance observed (anomaly ratio {anomaly_ratio * 100:.1f}%)."
        explanation = (
            "Localized recompression differences were observed. While sharp natural edges cause minor localized variance, "
            "the distribution shows moderate divergence that warrants closer inspection."
        )
    else:
        status = "LOW VARIATION"
        score = 2 if is_jpeg else 1
        finding = "Uniform recompression error distribution across all evaluated blocks."
        explanation = (
            "Error Level Analysis indicates a consistent compression rate across the image. "
            "No significant isolated patches with divergent compression artifacts were identified."
        )
        
    if not is_jpeg:
        explanation += (
            f" Note: Because the uploaded file is {file_format}, internal JPEG recompression was applied. "
            "Baseline rates reflect format conversion characteristics."
        )

    score = min(max_score, max(0, score))

    # Encode ELA visualization
    vis_data_uri = encode_cv2_to_base64_data_uri(visual_ela, "png")

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "reliability": reliability,
        "reliability_note": reliability_note,
        "source_compression": source_compression,
        "quality_tests": quality_tests,
        "metrics": {
            "global_mean_error": round(global_mean, 2),
            "global_std_error": round(global_std, 2),
            "max_pixel_diff": round(max_diff, 1),
            "anomalous_block_count": anomalous_blocks,
            "evaluated_blocks": total_blocks,
            "anomaly_ratio_pct": round(anomaly_ratio * 100, 2),
            "recompression_quality_test": 90,
            "sweep_quality_count": len(quality_tests)
        },
        "visualization": vis_data_uri
    }
