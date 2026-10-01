import uuid
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.validators import validate_image_file, MAX_FILE_SIZE_BYTES
from app.utils.image_utils import (
    safe_load_image,
    encode_pil_to_base64_data_uri,
    get_bounded_analysis_image
)
from app.services.file_analyzer import analyze_file_integrity
from app.services.metadata_analyzer import analyze_metadata
from app.services.ela_analyzer import analyze_ela
from app.services.copy_move_detector import detect_copy_move
from app.services.noise_analyzer import analyze_noise_consistency
from app.services.scoring_engine import calculate_forensic_assessment
from app.services.ml_detector import ml_detector

router = APIRouter(prefix="/api", tags=["forensic-analysis"])

import gc

CHUNK_SIZE = 64 * 1024  # 64 KB streaming chunks

# In-process concurrency guard: On a 512 MB Render instance, concurrent heavy analyses
# would multiply peak memory and trigger OOM. Serialize execution to guarantee memory safety.
ANALYSIS_SEMAPHORE = asyncio.Semaphore(1)


def _execute_pipeline(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """
    Synchronous CPU-intensive forensic analysis pipeline executed in an executor thread
    to ensure the ASGI event loop is never blocked.
    """
    # 1. Validation (MIME, magic bytes, dimensions, pixel count)
    is_valid, err_msg, file_info = validate_image_file(file_bytes, filename, content_type)
    if not is_valid:
        raise HTTPException(status_code=422, detail=err_msg)

    pil_rgb = None
    cv_bgr = None
    cv_gray = None
    analysis_pil = None
    cv_bgr_analysis = None
    cv_gray_analysis = None

    try:
        # 2. Safe Image Decoding (with early bounding for memory safety)
        try:
            pil_rgb, cv_bgr, cv_gray, orig_format = safe_load_image(file_bytes)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Image decoding failed: {str(e)}")

        # 3. Create bounded analysis representation for computationally heavy vision modules
        analysis_pil, cv_bgr_analysis, cv_gray_analysis, analysis_meta = get_bounded_analysis_image(
            pil_rgb, cv_bgr, cv_gray, max_dim=2048
        )

        analysis_id = str(uuid.uuid4())

        # 4. File Integrity & SHA-256 + Perceptual Hash
        file_result = analyze_file_integrity(file_bytes, file_info)

        # 5. Metadata / EXIF Forensics (uses original unscaled PIL image)
        try:
            metadata_result = analyze_metadata(pil_rgb, file_info)
        except Exception as e:
            metadata_result = {
                "score": 0,
                "max_score": 15,
                "status": "ANALYSIS ERROR",
                "finding": "Metadata parser encountered an unexpected tag structure.",
                "explanation": f"Non-standard metadata encoding prevented full extraction: {str(e)}",
                "details": {"has_exif": False, "camera": "Unavailable"}
            }

        # 6. Error Level Analysis (ELA) (uses bounded analysis image for memory and CPU safety)
        try:
            ela_result = analyze_ela(analysis_pil, cv_bgr_analysis, file_info.get("format", "JPEG"))
        except Exception as e:
            ela_result = {
                "score": 0,
                "max_score": 30,
                "status": "ANALYSIS ERROR",
                "finding": "ELA calculation could not be completed on this image buffer.",
                "explanation": f"Recompression analysis error: {str(e)}",
                "metrics": {},
                "visualization": ""
            }

        # 7. Copy-Move Forgery Detection with RANSAC Geometric Verification
        try:
            copy_move_result = detect_copy_move(cv_bgr_analysis, cv_gray_analysis)
        except Exception as e:
            copy_move_result = {
                "score": 0,
                "max_score": 30,
                "status": "ANALYSIS ERROR",
                "finding": "Feature matching could not process keypoints.",
                "explanation": f"Copy-move detector error: {str(e)}",
                "metrics": {
                    "keypoints_detected": 0,
                    "candidate_matches": 0,
                    "verified_matches": 0,
                    "coherent_clusters": 0,
                    "dominant_cluster_size": 0,
                    "geometric_cluster_evidence": "Detector exception."
                },
                "visualization": ""
            }

        # 8. Local Noise Consistency Analysis
        try:
            noise_result = analyze_noise_consistency(cv_bgr_analysis, cv_gray_analysis)
        except Exception as e:
            noise_result = {
                "score": 0,
                "max_score": 20,
                "status": "ANALYSIS ERROR",
                "finding": "Local noise analysis could not extract high-frequency residual.",
                "explanation": f"Noise variance calculation error: {str(e)}",
                "metrics": {},
                "visualization": ""
            }

        # 9. ML Tampering Detector (EfficientNet-B0) + Grad-CAM Explainability
        try:
            ml_result = ml_detector.predict(analysis_pil, cv_bgr_analysis)
        except Exception as e:
            ml_result = {
                "available": False,
                "prediction": None,
                "authentic_probability": None,
                "manipulated_probability": None,
                "confidence": None,
                "model": "EfficientNet-B0",
                "model_version": "pixelproof-casia-v1",
                "explanation": f"ML model inference failed: {str(e)}",
                "disclaimer": "ML classification failed for this image.",
                "metrics": {},
                "metadata": ml_detector.get_metadata()
            }

        # 10. Synthesis & Scoring Engine
        assessment = calculate_forensic_assessment(
            file_result=file_result,
            metadata_result=metadata_result,
            ela_result=ela_result,
            copy_move_result=copy_move_result,
            noise_result=noise_result,
            ml_result=ml_result
        )

        # Encode bounded preview for clean side-by-side comparison in UI
        original_preview_uri = encode_pil_to_base64_data_uri(analysis_pil, "JPEG")

        return {
            "analysis_id": analysis_id,
            "file": {
                "filename": file_info["filename"],
                "format": file_info["format"],
                "mime_type": file_info["mime_type"],
                "size": file_info["size"],
                "size_formatted": file_result["fingerprint"]["size_formatted"],
                "width": file_info["width"],
                "height": file_info["height"],
                "aspect_ratio": file_result["fingerprint"]["aspect_ratio"],
                "sha256": file_result["fingerprint"]["sha256"],
                "perceptual_hash": file_result["fingerprint"].get("perceptual_hash"),
                "timestamp": file_result["fingerprint"]["timestamp"]
            },
            "analysis_image": analysis_meta,
            "result": {
                "score": assessment["score"],
                "max_score": assessment["max_score"],
                "status": assessment["status"],
                "status_code": assessment["status_code"],
                "confidence": assessment["confidence"],
                "confidence_description": assessment["confidence_description"],
                "evidence_quality": assessment.get("evidence_quality", assessment["confidence"]),
                "evidence_quality_description": assessment.get(
                    "evidence_quality_description", assessment["confidence_description"]
                ),
                "summary": assessment["summary"],
                "disclaimer": assessment["disclaimer"],
                "breakdown": assessment["breakdown"]
            },
            "metadata": metadata_result,
            "ela": ela_result,
            "copy_move": copy_move_result,
            "noise": noise_result,
            "file_integrity": file_result,
            "ml_analysis": {
                "available": ml_result.get("available", False),
                "prediction": ml_result.get("prediction"),
                "signal_label": ml_result.get(
                    "signal_label",
                    "Manipulation-Leaning ML Signal" if ml_result.get("prediction") == "manipulated"
                    else ("Authenticity-Leaning ML Signal" if ml_result.get("prediction") == "authentic" else None)
                ),
                "authentic_probability": ml_result.get("authentic_probability"),
                "manipulated_probability": ml_result.get("manipulated_probability"),
                "confidence": ml_result.get("confidence"),
                "model": ml_result.get("model", "EfficientNet-B0"),
                "model_version": ml_result.get("model_version", "pixelproof-casia-v1"),
                "signal_type": ml_result.get("signal_type", "Independent ML Signal"),
                "explanation": ml_result.get("explanation"),
                "disclaimer": ml_result.get(
                    "disclaimer",
                    "This is an independent machine-learning signal, not the final forensic conclusion."
                ),
                "disagreement": assessment.get(
                    "evidence_disagreement", {"has_disagreement": False, "title": None, "message": None}
                ),
                "score_added": 0,
                "metrics": ml_result.get("metrics", {}),
                "metadata": ml_detector.get_metadata(),
                "gradcam": ml_result.get("gradcam", {"available": False, "explanation": "Grad-CAM not available."})
            },
            "evidence": assessment["evidence"],
            "original_preview": original_preview_uri
        }
    finally:
        # Guarantee all uncompressed image matrices are deleted and memory is reclaimed
        del pil_rgb, cv_bgr, cv_gray, analysis_pil, cv_bgr_analysis, cv_gray_analysis
        gc.collect()


@router.post("/analyze")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Executes the multi-engine forensic pipeline on an uploaded image with chunked streaming
    upload protection, in-process concurrency guard, and async threadpool offloading.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file was provided.")

    # P0-A: Chunked upload reading with EARLY byte counter
    # Halts immediately if payload exceeds 25 MB before buffering excessive bytes into memory.
    chunks = []
    total_bytes = 0
    try:
        while True:
            chunk = await file.read(CHUNK_SIZE)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Payload Too Large: Uploaded file exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
                )
            chunks.append(chunk)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded stream: {str(e)}")

    file_bytes = b"".join(chunks)

    # In-process concurrency guard: guarantee only 1 heavy analysis executes at a time on 512 MB instances
    async with ANALYSIS_SEMAPHORE:
        return await asyncio.to_thread(_execute_pipeline, file_bytes, file.filename or "uploaded_image", file.content_type)
