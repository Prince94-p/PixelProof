from PIL import Image, ExifTags
import re
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta

KNOWN_EDITORS = [
    "photoshop", "gimp", "lightroom", "canva", "snapseed", "pixlr", 
    "paint.net", "photopea", "affinity", "coreldraw", "pixelmator", 
    "procreate", "vsco", "facetune", "picsart", "afterfocus"
]

def parse_exif_timestamp(ts_str: str):
    """Parses standard EXIF timestamps (YYYY:MM:DD HH:MM:SS or YYYY-MM-DD HH:MM:SS)."""
    if not ts_str or not isinstance(ts_str, str):
        return None
    cleaned = ts_str.strip("\x00 \t\r\n")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

def check_timestamp_consistency(date_time: Optional[str] = None, date_original: Optional[str] = None, date_digitized: Optional[str] = None) -> dict:
    """
    Evaluates chronological consistency across standard EXIF timestamps:
    DateTime (modification), DateTimeOriginal (capture), DateTimeDigitized.
    """
    timestamp_flags = []
    ts_consistent = True
    chronological_order = "indeterminate"
    score_penalty = 0

    dt_mod = parse_exif_timestamp(date_time)
    dt_orig = parse_exif_timestamp(date_original)
    dt_dig = parse_exif_timestamp(date_digitized)

    # Check for malformed strings when strings were provided
    for label, raw_val, parsed_val in [("DateTime", date_time, dt_mod), ("DateTimeOriginal", date_original, dt_orig), ("DateTimeDigitized", date_digitized, dt_dig)]:
        if raw_val and isinstance(raw_val, str) and raw_val.strip() and not parsed_val:
            ts_consistent = False
            timestamp_flags.append(f"Malformed or non-standard timestamp format in tag {label}: {raw_val}")
            score_penalty += 2

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    future_boundary = now_utc + timedelta(days=2)

    has_any_ts = any([dt_mod, dt_orig, dt_dig])

    if has_any_ts:
        chronological_order = "valid"
        # Check future timestamps
        for label, dt_val in (("DateTime", dt_mod), ("DateTimeOriginal", dt_orig), ("DateTimeDigitized", dt_dig)):
            if dt_val and dt_val > future_boundary:
                ts_consistent = False
                score_penalty += 4
                timestamp_flags.append(f"Suspicious future timestamp recorded ({label}: {dt_val.strftime('%Y-%m-%d')}).")

        # Check chronological inversion (original capture must not be after modification)
        if dt_orig and dt_mod:
            if dt_orig > (dt_mod + timedelta(minutes=2)):
                ts_consistent = False
                chronological_order = "inverted"
                score_penalty += 4
                timestamp_flags.append(
                    f"Chronological inversion: Original capture timestamp ({dt_orig}) is later than modification timestamp ({dt_mod})."
                )
            elif dt_mod > dt_orig:
                timestamp_flags.append(
                    f"File post-processed/modified after original capture ({dt_mod - dt_orig} elapsed)."
                )

        if dt_orig and dt_dig:
            if dt_orig > (dt_dig + timedelta(minutes=2)):
                ts_consistent = False
                chronological_order = "inverted"
                score_penalty += 3
                timestamp_flags.append(
                    f"Chronological anomaly: Capture timestamp ({dt_orig}) is later than digitization timestamp ({dt_dig})."
                )

    return {
        "consistent": ts_consistent,
        "has_timestamps": has_any_ts,
        "chronological_order": chronological_order,
        "timestamp_flags": timestamp_flags,
        "score_penalty": min(6, score_penalty)
    }

def analyze_metadata(pil_img: Image.Image, file_info: dict) -> dict:
    """
    Extracts and evaluates EXIF, TIFF, and container metadata tags.
    Identifies camera hardware signatures, editing software traces,
    evaluates timestamp chronological consistency, and checks for metadata absence.
    """
    exif_data = {}
    
    # 1. Primary extraction via public getexif()
    try:
        if hasattr(pil_img, 'getexif') and callable(pil_img.getexif):
            exif_obj = pil_img.getexif()
            if exif_obj:
                for tag_id, value in exif_obj.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    exif_data[tag_name] = value

                # Also inspect sub-IFD (where DateTimeOriginal, DateTimeDigitized typically reside)
                if hasattr(ExifTags, 'IFD') and hasattr(ExifTags.IFD, 'Exif'):
                    try:
                        sub_ifd = exif_obj.get_ifd(ExifTags.IFD.Exif)
                        for sub_id, sub_val in sub_ifd.items():
                            sub_name = ExifTags.TAGS.get(sub_id, str(sub_id))
                            if sub_name not in exif_data:
                                exif_data[sub_name] = sub_val
                    except Exception:
                        pass
    except Exception:
        pass

    # Fallback to private _getexif() if getexif returned nothing
    if not exif_data:
        try:
            if hasattr(pil_img, '_getexif') and callable(pil_img._getexif):
                raw_exif = pil_img._getexif()
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                        exif_data[tag_name] = value
        except Exception:
            pass

    # Format values safely
    cleaned_exif = {}
    for tag_name, value in exif_data.items():
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8", errors="ignore").strip("\x00 \t\r\n")
            except Exception:
                value = str(value)
        elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int) and value[1] != 0:
            value = f"{value[0] / value[1]:.2f}"
        else:
            value = str(value).strip("\x00 \t\r\n")
        cleaned_exif[tag_name] = value

    exif_data = cleaned_exif

    # Also inspect PIL info (PNG tEXt chunks, JPEG comments, etc.)
    software_from_info = None
    if pil_img.info:
        for key, val in pil_img.info.items():
            if str(key).lower() in ("software", "tool", "comment", "description"):
                software_from_info = str(val)
                if "Software" not in exif_data:
                    exif_data["Software"] = software_from_info

    # Extract relevant fields
    make = exif_data.get("Make")
    model = exif_data.get("Model")
    software = exif_data.get("Software") or software_from_info
    date_time = exif_data.get("DateTime")
    date_original = exif_data.get("DateTimeOriginal")
    date_digitized = exif_data.get("DateTimeDigitized")
    orientation = exif_data.get("Orientation", "Standard")
    color_space = exif_data.get("ColorSpace")
    has_gps = "GPSInfo" in exif_data or any("gps" in k.lower() for k in exif_data.keys())

    # Format camera details
    camera_str = "Not recorded"
    if make or model:
        parts = [p for p in (make, model) if p]
        camera_str = " ".join(parts)

    # Check for photo editing software
    detected_editor = None
    if software:
        software_lower = software.lower()
        for editor in KNOWN_EDITORS:
            if editor in software_lower:
                detected_editor = software
                break

    # 2. Timestamp Chronological Consistency Evaluation
    ts_eval = check_timestamp_consistency(date_time, date_original, date_digitized)
    timestamp_flags = ts_eval["timestamp_flags"]
    ts_consistent = ts_eval["consistent"]
    chronological_order = ts_eval["chronological_order"]
    ts_score_penalty = ts_eval["score_penalty"]
    has_any_ts = ts_eval["has_timestamps"]

    # 3. Determine status, score, finding and explanation
    max_score = 15
    score = 0
    
    if not exif_data and not software:
        # Missing EXIF
        status = "METADATA UNAVAILABLE"
        score = 0
        finding = "No EXIF or hardware metadata detected in image."
        explanation = (
            "Metadata may have been removed during normal image processing (such as social media sharing, "
            "messaging applications, screenshots, or web recompression). Its absence alone is not evidence of manipulation."
        )
        has_exif = False
    elif detected_editor:
        # Software detected
        status = "REVIEW"
        score = 10
        finding = f"Editing software traces identified: {detected_editor}."
        explanation = (
            f"The image metadata explicitly records '{detected_editor}'. "
            "This confirms the file was processed or exported through desktop/mobile editing software rather than saved directly from a camera sensor."
        )
        if not ts_consistent:
            score = min(max_score, score + 3)
            explanation += " Additionally, timestamp inconsistencies were detected in EXIF headers."
        has_exif = True
    elif not ts_consistent and has_any_ts:
        # Inverted or future timestamps without software tag
        status = "REVIEW"
        score = 8
        finding = f"Timestamp anomaly detected: {timestamp_flags[0]}"
        explanation = (
            "Chronological inconsistencies found in header timestamps (e.g. future dates or original capture "
            "post-dating file modification). This indicates manual tag modification or clock displacement."
        )
        has_exif = True
    elif make or model:
        # Hardware camera tags present
        status = "CAMERA METADATA INTACT"
        score = 0
        finding = f"Hardware acquisition metadata found: {camera_str}."
        explanation = (
            f"Camera hardware identifiers ({camera_str}) and capture parameters are consistent with original hardware recording. "
            "No editing software signatures were present in the metadata blocks."
        )
        has_exif = True
    else:
        # Some generic metadata tags but no camera or editor
        status = "PARTIAL METADATA"
        score = 2
        finding = "Generic image metadata present without hardware camera identifiers."
        explanation = "The file contains standard color and dimension tags, but camera acquisition parameters are absent."
        has_exif = True

    score = min(max_score, max(0, score))

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "details": {
            "has_exif": has_exif,
            "camera": camera_str,
            "make": make or "Not recorded",
            "model": model or "Not recorded",
            "software": software or "None detected",
            "editor_detected": detected_editor,
            "date_time": date_time or "Not recorded",
            "date_original": date_original or "Not recorded",
            "date_digitized": date_digitized or "Not recorded",
            "orientation": str(orientation),
            "color_space": color_space or "sRGB / Standard",
            "gps_recorded": "Present (Protected)" if has_gps else "Not present",
            "raw_tags_count": len(exif_data),
            "timestamp_analysis": {
                "consistent": ts_consistent,
                "has_timestamps": has_any_ts,
                "chronological_order": chronological_order,
                "captured": date_original or "Not recorded",
                "modified": date_time or "Not recorded",
                "digitized": date_digitized or "Not recorded",
                "flags": timestamp_flags
            }
        }
    }
