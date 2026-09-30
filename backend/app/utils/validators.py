import io
import os
import re
from PIL import Image

ALLOWED_MIME_TYPES = {
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
    "image/webp": ["webp"]
}

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MIN_DIMENSION = 32
MAX_DIMENSION = 10000

def sanitize_filename(filename: str) -> str:
    """Removes unsafe characters and returns a clean basename."""
    if not filename:
        return "unnamed_image"
    clean_name = os.path.basename(filename)
    clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)
    return clean_name[:100]

def validate_image_file(file_bytes: bytes, filename: str, content_type: str = None) -> tuple[bool, str, dict]:
    """
    Validates actual image content:
    - Size checks
    - Header inspection
    - Pillow decode check
    - Dimension check
    Returns: (is_valid, error_message, file_info)
    """
    size = len(file_bytes)
    if size == 0:
        return False, "Uploaded file is completely empty (0 bytes).", {}
    
    if size > MAX_FILE_SIZE:
        return False, f"File size ({size / (1024 * 1024):.1f} MB) exceeds maximum allowed limit of 25 MB.", {}
    
    clean_fn = sanitize_filename(filename)
    ext = clean_fn.rsplit(".", 1)[-1].lower() if "." in clean_fn else ""
    
    # Try decoding header with Pillow
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            format_detected = (img.format or "").upper()
            width, height = img.size
            mode = img.mode
            
            # Map detected format to standard
            if format_detected in ("JPEG", "JPG"):
                canonical_format = "JPEG"
                canonical_mime = "image/jpeg"
            elif format_detected == "PNG":
                canonical_format = "PNG"
                canonical_mime = "image/png"
            elif format_detected == "WEBP":
                canonical_format = "WEBP"
                canonical_mime = "image/webp"
            else:
                return False, f"Unsupported image format '{format_detected}'. Only JPG, JPEG, PNG, and WEBP are supported.", {}

            if width < MIN_DIMENSION or height < MIN_DIMENSION:
                return False, f"Image dimensions ({width}x{height}) are too small for forensic analysis (minimum {MIN_DIMENSION}x{MIN_DIMENSION}px).", {}

            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                return False, f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of {MAX_DIMENSION}px.", {}

            # Verify entire image data can be parsed
            img.verify()
            
    except Exception as e:
        return False, f"Corrupted or invalid image file. Could not decode structure: {str(e)}", {}

    return True, "", {
        "filename": clean_fn,
        "format": canonical_format,
        "mime_type": canonical_mime,
        "size": size,
        "width": width,
        "height": height,
        "mode": mode
    }
