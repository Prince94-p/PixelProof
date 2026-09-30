from PIL import Image, ExifTags
import re

KNOWN_EDITORS = [
    "photoshop", "gimp", "lightroom", "canva", "snapseed", "pixlr", 
    "paint.net", "photopea", "affinity", "coreldraw", "pixelmator", 
    "procreate", "vsco", "facetune", "picsart", "afterfocus"
]

def analyze_metadata(pil_img: Image.Image, file_info: dict) -> dict:
    """
    Extracts and evaluates EXIF, TIFF, and container metadata tags.
    Identifies camera hardware signatures, editing software traces,
    and checks for metadata absence or inconsistencies.
    """
    exif_data = {}
    raw_exif = None
    
    # Try extracting EXIF
    try:
        if hasattr(pil_img, '_getexif') and callable(pil_img._getexif):
            raw_exif = pil_img._getexif()
    except Exception:
        raw_exif = None

    if raw_exif:
        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            # Format value safely
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8", errors="ignore").strip("\x00 \t\r\n")
                except Exception:
                    value = str(value)
            elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int) and value[1] != 0:
                # Rational number (e.g. aperture, focal length)
                value = f"{value[0] / value[1]:.2f}"
            else:
                value = str(value).strip("\x00 \t\r\n")
            
            exif_data[tag_name] = value

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

    # Determine status, score, finding and explanation
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
            "orientation": str(orientation),
            "color_space": color_space or "sRGB / Standard",
            "gps_recorded": "Present (Protected)" if has_gps else "Not present",
            "raw_tags_count": len(exif_data)
        }
    }
