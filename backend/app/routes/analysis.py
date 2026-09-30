import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.validators import validate_image_file
from app.utils.image_utils import safe_load_image, encode_pil_to_base64_data_uri
from app.services.file_analyzer import analyze_file_integrity
from app.services.metadata_analyzer import analyze_metadata
from app.services.ela_analyzer import analyze_ela
from app.services.copy_move_detector import detect_copy_move
from app.services.noise_analyzer import analyze_noise_consistency
from app.services.scoring_engine import calculate_forensic_assessment
from app.services.ml_detector import ml_detector

router = APIRouter(prefix="/api", tags=["forensic-analysis"])

@router.post("/analyze")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Executes the multi-engine forensic pipeline on an uploaded image:
    1. Validation (MIME, dimensions, decode)
    2. Cryptographic SHA-256 fingerprinting & file integrity
    3. EXIF & Metadata forensic inspection
    4. Error Level Analysis (ELA) with recompression discrepancy detection
    5. ORB-based Copy-Move cloning detection with vector clustering
    6. Local Noise Consistency Analysis with residual heatmap
    7. Optional ML detector inference (if exported weights provided)
    8. Evidence synthesis and initial evidence-weighted scoring
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file was provided.")

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    # 1. Validation
    is_valid, err_msg, file_info = validate_image_file(file_bytes, file.filename, file.content_type)
    if not is_valid:
        raise HTTPException(status_code=422, detail=err_msg)

    # 2. Safe Image Decoding
    try:
        pil_rgb, cv_bgr, cv_gray, orig_format = safe_load_image(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Image decoding failed: {str(e)}")

    analysis_id = str(uuid.uuid4())

    # 3. File Integrity & SHA-256 Fingerprint
    file_result = analyze_file_integrity(file_bytes, file_info)

    # 4. Metadata / EXIF Forensics
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

    # 5. Error Level Analysis (ELA)
    try:
        ela_result = analyze_ela(pil_rgb, cv_bgr, file_info.get("format", "JPEG"))
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

    # 6. Copy-Move Forgery Detection
    try:
        copy_move_result = detect_copy_move(cv_bgr, cv_gray)
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

    # 7. Local Noise Consistency Analysis
    try:
        noise_result = analyze_noise_consistency(cv_bgr, cv_gray)
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

    # 8. Optional ML Tampering Detector (EfficientNet-B0)
    try:
        ml_result = ml_detector.predict(pil_rgb, cv_bgr)
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

    # 9. Synthesis & Scoring Engine
    assessment = calculate_forensic_assessment(
        file_result=file_result,
        metadata_result=metadata_result,
        ela_result=ela_result,
        copy_move_result=copy_move_result,
        noise_result=noise_result,
        ml_result=ml_result
    )

    # Encode original preview for clean side-by-side comparison in UI
    original_preview_uri = encode_pil_to_base64_data_uri(pil_rgb, "JPEG")

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
            "timestamp": file_result["fingerprint"]["timestamp"]
        },
        "result": {
            "score": assessment["score"],
            "max_score": assessment["max_score"],
            "status": assessment["status"],
            "status_code": assessment["status_code"],
            "confidence": assessment["confidence"],
            "confidence_description": assessment["confidence_description"],
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
            "disclaimer": ml_result.get("disclaimer", "This is an independent machine-learning signal, not the final forensic conclusion."),
            "disagreement": assessment.get("evidence_disagreement", {"has_disagreement": False, "title": None, "message": None}),
            "score_added": 0,
            "metrics": ml_result.get("metrics", {}),
            "metadata": ml_detector.get_metadata()
        },
        "evidence": assessment["evidence"],
        "original_preview": original_preview_uri
    }
