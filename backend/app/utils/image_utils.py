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
