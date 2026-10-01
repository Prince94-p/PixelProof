import numpy as np
import cv2
from app.utils.image_utils import encode_cv2_to_base64_data_uri

def analyze_noise_consistency(cv_bgr: np.ndarray, cv_gray: np.ndarray) -> dict:
    """
    Performs block-based local noise variance analysis to identify spliced regions,
    airbrushed retouching, or inconsistent sensor noise floors across the image.
    """
    h, w = cv_gray.shape[:2]
    max_score = 20
    
    gray_f = cv_gray.astype(np.float32)
    
    # 1. High-frequency noise residual extraction
    # Subtracting Gaussian blur isolates fine sensor noise grain from underlying textures
    blur = cv2.GaussianBlur(gray_f, (5, 5), 1.0)
    residual = gray_f - blur
    del gray_f, blur  # Free immediately
    
    # 2. Block-based noise variance analysis
    block_size = max(24, min(48, min(h, w) // 16))
    blocks_y = max(1, h // block_size)
    blocks_x = max(1, w // block_size)
    
    noise_grid = np.zeros((blocks_y, blocks_x), dtype=np.float32)
    
    # Calculate edge magnitude map to suppress edge contamination in noise calculation
    sobelx = cv2.Sobel(cv_gray, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(cv_gray, cv2.CV_32F, 0, 1, ksize=3)
    edge_mag = cv2.magnitude(sobelx, sobely)
    del sobelx, sobely  # Free intermediate directional gradients immediately
    edge_thresh = np.percentile(edge_mag, 70)
    
    block_noises = []
    
    for by in range(blocks_y):
        for bx in range(blocks_x):
            y1 = by * block_size
            y2 = min(h, y1 + block_size)
            x1 = bx * block_size
            x2 = min(w, x1 + block_size)
            
            b_res = residual[y1:y2, x1:x2]
            b_edge = edge_mag[y1:y2, x1:x2]
            
            # Use non-edge pixels to measure pure sensor noise floor
            flat_mask = b_edge < edge_thresh
            if np.sum(flat_mask) > 16:
                samples = b_res[flat_mask]
            else:
                samples = b_res.flatten()
                
            # Median Absolute Deviation (MAD) for robust noise sigma estimation
            med = np.median(samples)
            mad = np.median(np.abs(samples - med))
            sigma_est = float(mad / 0.6745) if mad > 0 else float(np.std(samples))
            
            noise_grid[by, bx] = sigma_est
            block_noises.append(sigma_est)

    del residual, edge_mag  # Large 2D arrays no longer needed
    block_noises = np.array(block_noises)
    global_median_noise = float(np.median(block_noises))
    noise_iqr = float(np.percentile(block_noises, 75) - np.percentile(block_noises, 25))
    noise_cv = float(noise_iqr / (global_median_noise + 1e-4))  # Coefficient of quartile dispersion
    
    # 3. Detect Outliers (abnormally noisy or abnormally flat blocks)
    min_abs_delta = max(1.8 * noise_iqr, 1.2)
    abs_noise_diff = np.abs(block_noises - global_median_noise)
    outlier_count = int(np.sum(abs_noise_diff > min_abs_delta))
    total_blocks = len(block_noises)
    outlier_ratio = outlier_count / max(1, total_blocks)
    del abs_noise_diff

    # 4. Generate Professional Forensic Heatmap with Robust Absolute Reference
    min_ref_span = 2.5
    ref_min = max(0.0, global_median_noise - max(min_ref_span * 0.4, 2.5 * noise_iqr))
    ref_max = max(ref_min + min_ref_span, global_median_noise + max(min_ref_span * 0.6, 3.5 * noise_iqr))
    
    # Clip to robust reference bounds
    clipped_grid = np.clip(noise_grid, ref_min, ref_max)
    del noise_grid
    norm_grid = ((clipped_grid - ref_min) / (ref_max - ref_min) * 255.0).astype(np.uint8)
    del clipped_grid
    
    # Bound heatmap rendering resolution to max 1280px to prevent large temporary canvases
    max_render_dim = 1280
    if max(w, h) > max_render_dim:
        scale_v = max_render_dim / float(max(w, h))
        target_w = max(16, int(round(w * scale_v)))
        target_h = max(16, int(round(h * scale_v)))
        heatmap_resized = cv2.resize(norm_grid, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        gray_for_overlay = cv2.resize(cv_gray, (target_w, target_h), interpolation=cv2.INTER_AREA)
    else:
        heatmap_resized = cv2.resize(norm_grid, (w, h), interpolation=cv2.INTER_CUBIC)
        gray_for_overlay = cv_gray
    del norm_grid
    
    # Apply scientific colormap (COLORMAP_CIVIDIS is perceptually uniform and colorblind safe)
    colored_heatmap = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_CIVIDIS)
    del heatmap_resized
    
    # Blend with grayscale background (45% background, 55% heatmap)
    gray_bgr = cv2.cvtColor(gray_for_overlay, cv2.COLOR_GRAY2BGR)
    if gray_for_overlay is not cv_gray:
        del gray_for_overlay
    overlay = cv2.addWeighted(gray_bgr, 0.45, colored_heatmap, 0.55, 0)
    del gray_bgr, colored_heatmap
    
    vis_data_uri = encode_cv2_to_base64_data_uri(overlay, "png")
    del overlay

    # 5. Status & Initial Evidence Weight
    # If the image is extremely clean (noise floor is near 0, e.g. synthetic flat vector), dispersion is negligible
    is_very_clean_canvas = global_median_noise < 0.04

    if outlier_ratio > 0.08 and noise_cv > 0.55 and not is_very_clean_canvas:
        status = "STRONG LOCAL VARIATION"
        score = 15
        finding = f"High localized noise variance ({outlier_count} anomalous blocks, dispersion {noise_cv:.2f})."
        explanation = (
            "Notable disparities in local noise grain detected across different spatial zones. "
            "In natural photography, sensor noise is relatively uniform unless modified by localized blur, "
            "denoising filters, or splicing from an external image source."
        )
    elif (outlier_ratio > 0.04 or (noise_cv > 0.42 and outlier_count >= 3)) and not is_very_clean_canvas:
        status = "MODERATE VARIATION"
        score = 8
        finding = f"Moderate noise inconsistency observed across {outlier_count} evaluated blocks."
        explanation = (
            "Minor deviations in the local noise floor were recorded. This can occur naturally in scenes "
            "with steep optical depth-of-field (bokeh) or smooth sky gradients, but may also indicate mild localized retouching."
        )
    else:
        status = "MOSTLY CONSISTENT"
        score = 1
        finding = f"Uniform noise distribution across {total_blocks} blocks (dispersion {noise_cv:.2f})."
        explanation = (
            "Sensor noise residual is consistent across the entire image canvas. "
            "No isolated regions exhibiting artificial smoothing or contrasting sensor noise profiles were detected."
        )

    score = min(max_score, max(0, score))

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "visualization_note": "Heatmap visualizes local sensor noise variance relative to image-wide baseline. Warm tones reflect higher local noise dispersion, not confirmed manipulation.",
        "metrics": {
            "global_median_noise": round(global_median_noise, 3),
            "noise_iqr": round(noise_iqr, 3),
            "dispersion_cv": round(noise_cv, 2),
            "anomalous_blocks": outlier_count,
            "total_blocks": total_blocks,
            "outlier_ratio_pct": round(outlier_ratio * 100, 1),
            "block_dimension_px": block_size
        },
        "visualization": vis_data_uri
    }
