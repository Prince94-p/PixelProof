import io
import base64
import numpy as np
from PIL import Image, ImageOps
import cv2

def safe_load_image(image_bytes: bytes, max_analysis_dim: int = 2048):
    """
    Safely loads raw image bytes into:
    1. PIL Image (RGB) with EXIF orientation handled, bounded to max_analysis_dim.
    2. OpenCV BGR numpy array (bounded).
    3. OpenCV Grayscale numpy array (bounded).
    Avoids allocating massive uncompressed NumPy arrays for high-resolution images.
    """
    pil_img = Image.open(io.BytesIO(image_bytes))
    
    # Store original unscaled format and dimensions before any resize
    orig_format = pil_img.format or "JPEG"
    orig_w, orig_h = pil_img.size
    
    # Try EXIF transpose safely if orientation exists
    try:
        pil_img = ImageOps.exif_transpose(pil_img)
        # Update orig dimensions if rotated 90/270
        orig_w, orig_h = pil_img.size
    except Exception:
        pass

    # Early bounding: resize PIL image directly before allocating NumPy arrays
    longest = max(orig_w, orig_h)
    was_downscaled = False
    scale_factor = 1.0
    if longest > max_analysis_dim:
        scale_factor = max_analysis_dim / float(longest)
        bounded_w = max(32, int(round(orig_w * scale_factor)))
        bounded_h = max(32, int(round(orig_h * scale_factor)))
        pil_img = pil_img.resize((bounded_w, bounded_h), Image.Resampling.LANCZOS)
        was_downscaled = True
    
    # Ensure RGB
    if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
        # Convert transparent backgrounds to white to prevent dark artifacts in OpenCV
        rgba = pil_img.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        alpha_composite = Image.alpha_composite(background, rgba)
        rgb_img = alpha_composite.convert("RGB")
        del rgba, background, alpha_composite
    elif pil_img.mode != "RGB":
        rgb_img = pil_img.convert("RGB")
    else:
        rgb_img = pil_img.copy()

    # Attach original dimensions metadata attribute for downstream consumers
    setattr(rgb_img, "orig_dimensions", (orig_w, orig_h))
    setattr(rgb_img, "was_early_bounded", was_downscaled)
    setattr(rgb_img, "early_scale_factor", round(scale_factor, 4))

    # Convert bounded image to OpenCV BGR and Grayscale
    cv_rgb = np.array(rgb_img)
    cv_bgr = cv2.cvtColor(cv_rgb, cv2.COLOR_RGB2BGR)
    cv_gray = cv2.cvtColor(cv_bgr, cv2.COLOR_BGR2GRAY)
    del cv_rgb  # Release intermediate RGB numpy array immediately

    return rgb_img, cv_bgr, cv_gray, orig_format

def encode_cv2_to_base64_data_uri(cv_img: np.ndarray, format_ext: str = "png", max_dim: int = 1280) -> str:
    """
    Encodes an OpenCV image (BGR) into a base64 data URI (data:image/png;base64,...).
    Bounds visualization dimension to max_dim to avoid giant base64 buffers on 512 MB instances.
    """
    h, w = cv_img.shape[:2]
    longest = max(h, w)
    if longest > max_dim:
        scale = max_dim / float(longest)
        new_w = max(16, int(round(w * scale)))
        new_h = max(16, int(round(h * scale)))
        target_img = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        target_img = cv_img

    success, encoded_img = cv2.imencode(f".{format_ext}", target_img)
    if not success:
        raise ValueError("Failed to encode image to base64")

    b64_bytes = encoded_img.tobytes()
    del encoded_img
    b64_str = base64.b64encode(b64_bytes).decode("utf-8")
    del b64_bytes
    return f"data:image/{format_ext};base64,{b64_str}"

def encode_pil_to_base64_data_uri(pil_img: Image.Image, format_str: str = "PNG", max_dim: int = 1280) -> str:
    """
    Encodes a PIL image into a base64 data URI.
    Bounds preview dimension to max_dim to prevent high memory usage.
    """
    orig_w, orig_h = pil_img.size
    longest = max(orig_w, orig_h)
    if longest > max_dim:
        scale = max_dim / float(longest)
        new_w = max(16, int(round(orig_w * scale)))
        new_h = max(16, int(round(orig_h * scale)))
        img_to_encode = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    else:
        img_to_encode = pil_img

    buffer = io.BytesIO()
    if format_str.upper() in ("JPG", "JPEG"):
        if img_to_encode.mode in ("RGBA", "P"):
            img_to_encode = img_to_encode.convert("RGB")
        img_to_encode.save(buffer, format="JPEG", quality=88)
        mime = "jpeg"
    else:
        img_to_encode.save(buffer, format="PNG")
        mime = "png"
    
    b64_bytes = buffer.getvalue()
    buffer.close()
    del buffer
    b64_str = base64.b64encode(b64_bytes).decode("utf-8")
    del b64_bytes
    return f"data:image/{mime};base64,{b64_str}"

def get_bounded_analysis_image(pil_rgb: Image.Image, cv_bgr: np.ndarray, cv_gray: np.ndarray, max_dim: int = 2048):
    """
    Produces a safely bounded image representation for computationally expensive
    vision routines (ORB, ELA, noise maps) without altering original full-size image bytes.
    Does NOT upscale smaller images.
    Returns: (analysis_pil, analysis_bgr, analysis_gray, analysis_meta)
    """
    # Check if safe_load_image already bounded this image
    orig_dim = getattr(pil_rgb, "orig_dimensions", None)
    was_early = getattr(pil_rgb, "was_early_bounded", False)
    
    if orig_dim is not None and was_early:
        orig_w, orig_h = orig_dim
        scale = getattr(pil_rgb, "early_scale_factor", round(max_dim / float(max(orig_w, orig_h)), 4))
        cur_w, cur_h = pil_rgb.size
        return pil_rgb, cv_bgr, cv_gray, {
            "downscaled": True,
            "original_width": orig_w,
            "original_height": orig_h,
            "analysis_width": cur_w,
            "analysis_height": cur_h,
            "scale_factor": scale
        }

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
