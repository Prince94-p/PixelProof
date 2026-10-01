import io
import base64
import numpy as np
from PIL import Image, ImageOps
import cv2

def safe_load_image(image_bytes: bytes):
    """
    Safely loads raw image bytes into:
    1. PIL Image (RGB) with EXIF orientation handled.
    2. OpenCV BGR numpy array.
    3. OpenCV Grayscale numpy array.
    """
    pil_img = Image.open(io.BytesIO(image_bytes))
    
    # Store original format before transpose
    orig_format = pil_img.format or "JPEG"
    
    # Try EXIF transpose safely if orientation exists
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass
    
    # Ensure RGB
    if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
        # Convert transparent backgrounds to white to prevent dark artifacts in OpenCV
        rgba = pil_img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        alpha_composite = Image.alpha_composite(background, rgba)
        rgb_img = alpha_composite.convert("RGB")
    elif pil_img.mode != "RGB":
        rgb_img = pil_img.convert("RGB")
    else:
        rgb_img = pil_img.copy()

    # Convert to OpenCV BGR
    cv_rgb = np.array(rgb_img)
    cv_bgr = cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)
    cv_gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)

    return rgb_img, cv_bgr, cv_gray, orig_format

def encode_cv2_to_base64_data_uri(cv_img: np.ndarray, format_ext: str = "png") -> str:
    """
    Encodes an OpenCV image (BGR) into a base64 data URI (data:image/png;base64,...).
    """
    if len(cv_img.shape) == 2:
        # Grayscale
        success, encoded_img = cv2.imencode(f".{format_ext}", cv_img)
    elif cv_img.shape[2] == 3:
        # BGR
        success, encoded_img = cv2.imencode(f".{format_ext}", cv_img)
    elif cv_img.shape[2] == 4:
        # BGRA
        success, encoded_img = cv2.imencode(f".{format_ext}", cv_img)
    else:
        success, encoded_img = cv2.imencode(f".{format_ext}", cv_img)

    if not success:
        raise ValueError("Failed to encode image to base64")

    b64_str = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    return f"data:image/{format_ext};base64,{b64_str}"

def encode_pil_to_base64_data_uri(pil_img: Image.Image, format_str: str = "PNG") -> str:
    """
    Encodes a PIL image into a base64 data URI.
    """
    buffer = io.BytesIO()
    # Save as PNG or JPEG
    if format_str.upper() in ("JPG", "JPEG"):
        if pil_img.mode in ("RGBA", "P"):
            pil_img = pil_img.convert("RGB")
        pil_img.save(buffer, format="JPEG", quality=92)
        mime = "jpeg"
    else:
        pil_img.save(buffer, format="PNG")
        mime = "png"
    
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{mime};base64,{b64_str}"

def get_bounded_analysis_image(pil_rgb: Image.Image, cv_bgr: np.ndarray, cv_gray: np.ndarray, max_dim: int = 2048):
    """
    Produces a safely bounded image representation for computationally expensive
    vision routines (ORB, ELA, noise maps) without altering original full-size image bytes.
    Does NOT upscale smaller images.
    Returns: (analysis_pil, analysis_bgr, analysis_gray, analysis_meta)
    """
    orig_w, orig_h = pil_rgb.size
    longest = max(orig_w, orig_h)
    
    if longest <= max_dim:
        return pil_rgb, cv_bgr, cv_gray, {
            "downscaled": False,
            "original_width": orig_w,
            "original_height": orig_h,
            "analysis_width": orig_w,
            "analysis_height": orig_h,
            "scale_factor": 1.0
        }
    
    scale = max_dim / float(longest)
    new_w = max(32, int(round(orig_w * scale)))
    new_h = max(32, int(round(orig_h * scale)))
    
    # Resize PIL RGB
    analysis_pil = pil_rgb.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Resize OpenCV matrices with INTER_AREA (optimal for downsampling)
    analysis_bgr = cv2.resize(cv_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    analysis_gray = cv2.resize(cv_gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    analysis_meta = {
        "downscaled": True,
        "original_width": orig_w,
        "original_height": orig_h,
        "analysis_width": new_w,
        "analysis_height": new_h,
        "scale_factor": round(scale, 4)
    }
    
    return analysis_pil, analysis_bgr, analysis_gray, analysis_meta

def compute_perceptual_hash(image_input) -> str:
    """
    Computes a standard 64-bit DCT perceptual hash (pHash) for visual similarity matching.
    Accepts PIL.Image, numpy ndarray (grayscale/color), or raw image bytes.
    Robust against minor recompression, scaling, and format shifts.
    """
    try:
        if image_input is None:
            return "0000000000000000"

        if isinstance(image_input, bytes):
            pil_img = Image.open(io.BytesIO(image_input)).convert("L")
            cv_gray = np.array(pil_img)
        elif isinstance(image_input, Image.Image):
            cv_gray = np.array(image_input.convert("L"))
        elif isinstance(image_input, np.ndarray):
            if image_input.ndim == 3:
                cv_gray = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
            else:
                cv_gray = image_input
        else:
            return "0000000000000000"

        # Resize to 32x32
        resized = cv2.resize(cv_gray, (32, 32), interpolation=cv2.INTER_AREA)
        # Compute 2D Discrete Cosine Transform
        dct = cv2.dct(np.float32(resized))
        # Extract top-left 8x8 lowest frequencies
        dct_low = dct[:8, :8]
        # Median of AC components (exclude DC component at [0,0])
        med = float(np.median(dct_low[1:, 1:])) if dct_low.size > 1 else float(np.median(dct_low))
        # Compute 64-bit binary sequence
        bits = (dct_low > med).flatten()
        hash_int = 0
        for b in bits:
            hash_int = (hash_int << 1) | int(b)
        return f"{hash_int:016x}"
    except Exception:
        # Fallback to zero hash on unexpected failure
        return "0000000000000000"
