from typing import Optional, Dict, Any

def check_evidence_disagreement(score: int, status: str, ml_result: Optional[dict]) -> dict:
    """
    Evaluates whether the independent ML classification signal and classical forensic
    evidence disagree, providing contextual explanation for manual review without
    altering the classical forensic score or verdict.
    """
    if not ml_result or not ml_result.get("available") or not ml_result.get("prediction"):
        return {
            "has_disagreement": False,
            "title": None,
            "message": None,
        }

    ml_pred = ml_result.get("prediction")
    has_disagreement = False
    message = ""

    if ml_pred == "manipulated" and (score < 30 or status == "Low Suspicion"):
        has_disagreement = True
        message = (
            "The ML classifier detected manipulation-associated visual patterns, "
            "while classical forensic modules found limited direct manipulation evidence. "
            "Manual review is recommended when independent signals disagree."
        )
    elif ml_pred == "authentic" and (score >= 60 or status == "Strong Manipulation Indicators"):
        has_disagreement = True
        message = (
            "Classical forensic modules detected strong manipulation indicators, "
            "while the ML classifier produced an authenticity-leaning visual pattern signal. "
            "Manual review is recommended when independent signals disagree."
        )
    elif ml_pred == "authentic" and score >= 30:
        has_disagreement = True
        message = (
            "Classical forensic modules identified indicators warranting review, "
            "while the ML classifier produced an authenticity-leaning visual pattern signal. "
            "Manual review is recommended when independent signals disagree."
        )

    return {
        "has_disagreement": has_disagreement,
        "title": "EVIDENCE DISAGREEMENT" if has_disagreement else None,
        "message": message if has_disagreement else None,
    }


def calculate_forensic_assessment(
    file_result: dict,
    metadata_result: dict,
    ela_result: dict,
    copy_move_result: dict,
    noise_result: dict,
    ml_result: Optional[dict] = None
) -> dict:
    """
    Synthesizes independent forensic results into an initial evidence-weighted suspicion score (0-100),
    confidence rating, and itemized explainable evidence list.
    
    IMPORTANT: Weights (15/30/30/20/5) and thresholds (0-29/30-59/60-100) are initial heuristic evidence
    weights and are NOT described as dataset calibrated until real benchmark calibration is performed.

    The ML classifier output is an independent signal and is NEVER added directly into the 0-100 forensic score.
    """
    file_score = min(5, max(0, file_result.get("score", 0)))
    meta_score = min(15, max(0, metadata_result.get("score", 0)))
    ela_score = min(30, max(0, ela_result.get("score", 0)))
    cm_score = min(30, max(0, copy_move_result.get("score", 0)))
    noise_score = min(20, max(0, noise_result.get("score", 0)))

    # Primary Forensic Suspicion Score stays strictly composed of the 5 classical forensic modules:
    # Metadata (15) + ELA (30) + Copy-Move (30) + Noise (20) + File Integrity (5) = 100 max
    total_score = file_score + meta_score + ela_score + cm_score + noise_score
    total_score = max(0, min(100, int(round(total_score))))

    # Determine status & color coding
    if total_score >= 60:
        status_label = "Strong Manipulation Indicators"
        status_code = "danger"  # Red
        summary = (
            "Multiple distinct forensic indicators exhibit strong anomalies. "
            "Corroborating traces across independent analyses suggest significant post-processing, cloning, or localized manipulation."
        )
    elif total_score >= 30:
        status_label = "Review Recommended"
        status_code = "warning"  # Amber
        summary = (
            "Several forensic indicators warrant closer inspection. "
            "While natural factors like compression or repetitive patterns can cause minor divergence, "
            "the detected traces justify manual review."
        )
    else:
        status_label = "Low Suspicion"
        status_code = "success"  # Green
        summary = (
            "Forensic analysis across metadata, recompression error levels, cloning vectors, and noise consistency "
            "demonstrated uniform consistency with no strong indicators of digital manipulation."
        )

    # Calculate forensic confidence level (Low, Moderate, High)
    # Based on evidence density, file size, format, and cross-module agreement
    evidence_points = 0
    anomalous_modules = sum([
        1 if meta_score >= 8 else 0,
        1 if ela_score >= 12 else 0,
        1 if cm_score >= 10 else 0,
        1 if noise_score >= 8 else 0,
        1 if file_score >= 3 else 0,
    ])

    file_info = file_result.get("fingerprint", {})
    pixel_count = file_info.get("width", 0) * file_info.get("height", 0)
    has_exif = metadata_result.get("details", {}).get("has_exif", False)

    if pixel_count >= 500000:
        evidence_points += 1
    if pixel_count >= 1500000:
        evidence_points += 1
    if has_exif:
        evidence_points += 1
    if anomalous_modules >= 2:
        evidence_points += 2  # Cross-corroboration
    elif anomalous_modules == 0 and pixel_count >= 800000:
        evidence_points += 2  # Strong baseline consistency across large image

    if evidence_points >= 4:
        confidence = "High"
        confidence_desc = "High confidence based on substantial pixel volume, independent cross-checks, and corroborated findings."
        evidence_quality = "High"
        evidence_quality_desc = "High evidence quality based on substantial pixel volume, independent cross-checks, and corroborated forensic indicators. Evidence quality reflects available forensic information, not statistical accuracy probability."
    elif evidence_points >= 2:
        confidence = "Moderate"
        confidence_desc = "Moderate confidence based on standard evidence availability and typical recompression constraints."
        evidence_quality = "Moderate"
        evidence_quality_desc = "Moderate evidence quality based on standard evidence availability and typical recompression constraints. Evidence quality reflects available forensic information, not statistical accuracy probability."
    else:
        confidence = "Low"
        confidence_desc = "Low confidence due to constrained image resolution or limited metadata context."
        evidence_quality = "Low"
        evidence_quality_desc = "Low evidence quality due to constrained image resolution or limited metadata context. Evidence quality reflects available forensic information, not statistical accuracy probability."

    # Build explainable evidence breakdown list
    evidence_list = [
        {
            "id": 1,
            "module": "Metadata & EXIF Analysis",
            "status": metadata_result.get("status", "UNAVAILABLE"),
            "status_type": "danger" if meta_score >= 10 else ("warning" if meta_score > 0 else "success"),
            "score": meta_score,
            "max_score": 15,
            "finding": metadata_result.get("finding", ""),
            "explanation": metadata_result.get("explanation", ""),
            "corroborated": meta_score >= 8 and (ela_score >= 12 or cm_score >= 10)
        },
        {
            "id": 2,
            "module": "Error Level Analysis (ELA)",
            "status": ela_result.get("status", "LOW VARIATION"),
            "status_type": "danger" if ela_score >= 20 else ("warning" if ela_score >= 10 else "success"),
            "score": ela_score,
            "max_score": 30,
            "finding": ela_result.get("finding", ""),
            "explanation": ela_result.get("explanation", ""),
            "corroborated": ela_score >= 12 and (cm_score >= 10 or noise_score >= 8)
        },
        {
            "id": 3,
            "module": "Copy-Move Cloning Detection",
            "status": copy_move_result.get("status", "NO DUPLICATED REGIONS DETECTED"),
            "status_type": "danger" if cm_score >= 18 else ("warning" if cm_score >= 8 else "success"),
            "score": cm_score,
            "max_score": 30,
            "finding": copy_move_result.get("finding", ""),
            "explanation": copy_move_result.get("explanation", ""),
            "corroborated": cm_score >= 10 and (ela_score >= 12)
        },
        {
            "id": 4,
            "module": "Noise Consistency Analysis",
            "status": noise_result.get("status", "MOSTLY CONSISTENT"),
            "status_type": "danger" if noise_score >= 14 else ("warning" if noise_score >= 8 else "success"),
            "score": noise_score,
            "max_score": 20,
            "finding": noise_result.get("finding", ""),
            "explanation": noise_result.get("explanation", ""),
            "corroborated": noise_score >= 8 and (ela_score >= 12)
        },
        {
            "id": 5,
            "module": "File Integrity & Container Verification",
            "status": file_result.get("status", "VALID"),
            "status_type": "danger" if file_score >= 4 else "success",
            "score": file_score,
            "max_score": 5,
            "finding": file_result.get("finding", ""),
            "explanation": file_result.get("explanation", ""),
            "corroborated": False
        }
    ]

    disagreement = check_evidence_disagreement(total_score, status_label, ml_result)

    return {
        "score": total_score,
        "max_score": 100,
        "status": status_label,
        "status_code": status_code,
        "confidence": confidence,
        "confidence_description": confidence_desc,
        "evidence_quality": evidence_quality,
        "evidence_quality_description": evidence_quality_desc,
        "summary": summary,
        "disclaimer": "This score represents the strength of detected forensic indicators based on initial evidence weights (15/30/30/20/5). It is not the probability that the image is fake.",
        "breakdown": {
            "metadata": {"score": meta_score, "max": 15},
            "ela": {"score": ela_score, "max": 30},
            "copy_move": {"score": cm_score, "max": 30},
            "noise": {"score": noise_score, "max": 20},
            "file_integrity": {"score": file_score, "max": 5},
            "total": {"score": total_score, "max": 100}
        },
        "evidence": evidence_list,
        "evidence_disagreement": disagreement
    }
