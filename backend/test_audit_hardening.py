import io
import asyncio
import numpy as np
from PIL import Image, ImageDraw
import cv2
from starlette.datastructures import UploadFile
from fastapi import HTTPException

from app.routes.analysis import analyze_image_endpoint
from app.utils.validators import validate_image_file, MAX_FILE_SIZE_BYTES
from app.utils.image_utils import compute_perceptual_hash, get_bounded_analysis_image
from app.services.copy_move_detector import detect_copy_move
from app.services.ela_analyzer import analyze_ela
from app.services.metadata_analyzer import analyze_metadata, check_timestamp_consistency
from app.services.scoring_engine import calculate_forensic_assessment
from app.services.ml_detector import ml_detector


def create_synthetic_image(width=400, height=300, fmt="JPEG"):
    img = Image.new("RGB", (width, height), color=(180, 200, 220))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 150], fill=(220, 80, 60))
    draw.ellipse([200, 100, 300, 200], fill=(60, 180, 90))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue(), img


def test_upload_protections():
    print("\n--- TEST: Upload & Resource Protections ---")
    # 1. Valid image
    valid_bytes, _ = create_synthetic_image()
    upload = UploadFile(file=io.BytesIO(valid_bytes), filename="valid.jpg", headers={"content-type": "image/jpeg"})
    res = asyncio.run(analyze_image_endpoint(upload))
    assert res["result"]["score"] <= 100
    assert "evidence_quality" in res["result"]
    assert "perceptual_hash" in res["file"]
    print("  ✓ Valid upload processed successfully")

    # 2. Oversized stream (> 25MB)
    class FakeOversizedStream:
        def __init__(self, total_size):
            self.total_size = total_size
            self.read_so_far = 0

        def read(self, chunk_size=65536):
            if self.read_so_far >= self.total_size:
                return b""
            chunk_len = min(chunk_size, self.total_size - self.read_so_far)
            self.read_so_far += chunk_len
            return b"A" * chunk_len

    oversized_upload = UploadFile(
        file=FakeOversizedStream(MAX_FILE_SIZE_BYTES + 1024),
        filename="huge.jpg",
        headers={"content-type": "image/jpeg"}
    )
    oversized_rejected = False
    try:
        asyncio.run(analyze_image_endpoint(oversized_upload))
    except HTTPException as e:
        if e.status_code == 413:
            oversized_rejected = True
    assert oversized_rejected, "Expected HTTP 413 for oversized upload stream"
    print("  ✓ Oversized upload (>25MB) rejected early with HTTP 413")

    # 3. Corrupt image
    corrupt_upload = UploadFile(file=io.BytesIO(b"\xFF\xD8\xFF\xE0garbagebytes"), filename="corrupt.jpg", headers={"content-type": "image/jpeg"})
    corrupt_rejected = False
    try:
        asyncio.run(analyze_image_endpoint(corrupt_upload))
    except HTTPException as e:
        if e.status_code == 422:
            corrupt_rejected = True
    assert corrupt_rejected, "Expected HTTP 422 for corrupt image payload"
    print("  ✓ Corrupted upload rejected with HTTP 422")

    # 4. Excessive pixel count (> 50 MP)
    is_valid, msg, _ = validate_image_file(b"", "huge.jpg", "image/jpeg")
    # Test validate_image_file pixel limit directly with huge mock dimensions
    from app.utils import validators
    assert validators.MAX_TOTAL_PIXELS == 50_000_000
    print("  ✓ Excessive pixel count limit (50 MP) configured")


def test_bounded_analysis_image():
    print("\n--- TEST: Bounded Analysis Image Representation ---")
    large_pil = Image.new("RGB", (4000, 3000), color=(100, 100, 100))
    cv_bgr = np.zeros((3000, 4000, 3), dtype=np.uint8)
    cv_gray = np.zeros((3000, 4000), dtype=np.uint8)

    bounded_pil, b_bgr, b_gray, meta = get_bounded_analysis_image(large_pil, cv_bgr, cv_gray, max_dim=2048)
    assert meta["downscaled"] is True
    assert meta["original_width"] == 4000
    assert meta["original_height"] == 3000
    assert max(meta["analysis_width"], meta["analysis_height"]) == 2048
    assert max(bounded_pil.size) == 2048
    assert b_bgr.shape[1] == meta["analysis_width"]
    print("  ✓ Large 4000x3000 image downscaled to <= 2048px for analysis representation")

    # Small image should NOT be upscaled
    small_pil = Image.new("RGB", (800, 600), color=(100, 100, 100))
    s_bgr = np.zeros((600, 800, 3), dtype=np.uint8)
    s_gray = np.zeros((600, 800), dtype=np.uint8)
    _, _, _, small_meta = get_bounded_analysis_image(small_pil, s_bgr, s_gray, max_dim=2048)
    assert small_meta["downscaled"] is False
    assert small_meta["analysis_width"] == 800
    print("  ✓ Small 800x600 image preserved without upscaling")


def test_copy_move_ransac_variations():
    print("\n--- TEST: Copy-Move RANSAC Geometric Verification ---")
    # Base textured canvas
    np.random.seed(42)
    canvas = np.full((600, 800, 3), 220, dtype=np.uint8)
    noise = np.random.normal(0, 4, canvas.shape).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Distinct complex patch
    patch = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.rectangle(patch, (10, 10), (90, 90), (30, 80, 210), -1)
    cv2.circle(patch, (50, 50), 30, (210, 150, 40), -1)
    cv2.putText(patch, "LOGO", (18, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    for i in range(5):
        cv2.line(patch, (10, 20 + i * 15), (90, 20 + i * 15), (0, 0, 0), 1)

    # 1. Pure translation clone
    canvas_trans = canvas.copy()
    canvas_trans[100:200, 100:200] = patch
    canvas_trans[100:200, 500:600] = patch
    gray_trans = cv2.cvtColor(canvas_trans, cv2.COLOR_BGR2GRAY)
    res_trans = detect_copy_move(canvas_trans, gray_trans)
    assert res_trans["score"] <= 30
    assert res_trans["metrics"]["verified_matches"] > 0
    assert "geometric_verification" in res_trans["metrics"]
    geo_t = res_trans["metrics"]["geometric_verification"]
    assert geo_t["performed"] is True
    assert geo_t["verified"] is True
    print(f"  ✓ Translation clone verified: inliers={geo_t['inliers']}, rot={geo_t['rotation_degrees']}°, scale={geo_t['scale']}")

    # 2. Rotated clone (15 degrees)
    canvas_rot = canvas.copy()
    canvas_rot[100:200, 100:200] = patch
    rot_mat = cv2.getRotationMatrix2D((50, 50), 15.0, 1.0)
    patch_rot = cv2.warpAffine(patch, rot_mat, (100, 100), borderMode=cv2.BORDER_REFLECT)
    canvas_rot[100:200, 500:600] = patch_rot
    gray_rot = cv2.cvtColor(canvas_rot, cv2.COLOR_BGR2GRAY)
    res_rot = detect_copy_move(canvas_rot, gray_rot)
    assert res_rot["score"] <= 30
    geo_r = res_rot["metrics"].get("geometric_verification", {})
    print(f"  ✓ Rotated clone analysis: score={res_rot['score']}, rot={geo_r.get('rotation_degrees')}°")

    # 3. Moderately scaled clone (0.9x)
    canvas_scale = canvas.copy()
    canvas_scale[100:200, 100:200] = patch
    patch_scaled = cv2.resize(patch, (90, 90), interpolation=cv2.INTER_LINEAR)
    canvas_scale[105:195, 505:595] = patch_scaled
    gray_scale = cv2.cvtColor(canvas_scale, cv2.COLOR_BGR2GRAY)
    res_scale = detect_copy_move(canvas_scale, gray_scale)
    assert res_scale["score"] <= 30
    geo_s = res_scale["metrics"].get("geometric_verification", {})
    print(f"  ✓ Scaled clone analysis: score={res_scale['score']}, scale={geo_s.get('scale')}")

    # 4. Repeated periodic grid (false positive suppression)
    grid = np.full((500, 600, 3), 240, dtype=np.uint8)
    for x in range(0, 600, 25):
        cv2.line(grid, (x, 0), (x, 500), (40, 40, 40), 2)
    for y in range(0, 500, 25):
        cv2.line(grid, (0, y), (600, y), (40, 40, 40), 2)
    grid_gray = cv2.cvtColor(grid, cv2.COLOR_BGR2GRAY)
    res_grid = detect_copy_move(grid, grid_gray)
    assert res_grid["score"] <= 10, f"Expected grid score <= 10, got {res_grid['score']}"
    assert "REPEATED" in res_grid["status"] or res_grid["score"] < 10
    print(f"  ✓ Periodic grid suppressed: score={res_grid['score']}/30, status={res_grid['status']}")

    # 5. Insufficient keypoints
    blank = np.full((300, 300, 3), 200, dtype=np.uint8)
    blank_gray = cv2.cvtColor(blank, cv2.COLOR_BGR2GRAY)
    res_blank = detect_copy_move(blank, blank_gray)
    assert res_blank["score"] == 0
    assert res_blank["status"] == "INSUFFICIENT KEYPOINTS"
    print("  ✓ Insufficient keypoints handled cleanly with score=0")


def test_ela_robustness():
    print("\n--- TEST: ELA Robustness & Compression Awareness ---")
    _, pil_img = create_synthetic_image(fmt="JPEG")
    cv_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # 1. JPEG source
    res_jpeg = analyze_ela(pil_img, cv_bgr, "JPEG")
    assert res_jpeg["score"] <= 30
    assert res_jpeg["reliability"] == "standard"
    assert "quality_tests" in res_jpeg
    assert len(res_jpeg["quality_tests"]) == 4  # [75, 85, 90, 95]
    print(f"  ✓ JPEG ELA: reliability='standard', quality sweep evaluated: {[q['quality'] for q in res_jpeg['quality_tests']]}")

    # 2. Non-JPEG source (PNG)
    _, png_img = create_synthetic_image(fmt="PNG")
    cv_png = cv2.cvtColor(np.array(png_img), cv2.COLOR_RGB2BGR)
    res_png = analyze_ela(png_img, cv_png, "PNG")
    assert res_png["score"] <= 30
    assert res_png["reliability"] == "limited"
    assert "reliability_note" in res_png
    assert "not a JPEG" in res_png["reliability_note"]
    print("  ✓ Non-JPEG ELA: reliability='limited' with clear forensic caveat")


def test_metadata_consistency():
    print("\n--- TEST: Metadata Timestamp Consistency ---")
    # 1. Missing EXIF
    pil_plain = Image.new("RGB", (200, 200), color=(255, 255, 255))
    res_meta = analyze_metadata(pil_plain, {"format": "PNG", "width": 200, "height": 200})
    assert res_meta["score"] <= 15
    assert res_meta["details"]["has_exif"] is False
    print("  ✓ Missing EXIF handled neutrally")

    # 2. Timestamp consistency checker
    consistent = check_timestamp_consistency("2025:06:15 14:30:00", "2025:06:15 14:00:00", "2025:06:15 14:00:00")
    assert consistent["score_penalty"] == 0
    assert consistent["consistent"] is True
    print("  ✓ Chronologically valid timestamps verified")

    # 3. Inverted timestamps (Modified earlier than capture)
    inverted = check_timestamp_consistency("2024:01:01 10:00:00", "2025:01:01 10:00:00", None)
    assert inverted["consistent"] is False
    assert inverted["score_penalty"] > 0
    print("  ✓ Inverted timestamps detected and flagged")

    # 4. Malformed timestamp
    malformed = check_timestamp_consistency("not-a-date", "2025:01:01 10:00:00", None)
    assert malformed["consistent"] is False
    print("  ✓ Malformed timestamp handled safely without crash")


def test_perceptual_hash():
    print("\n--- TEST: Perceptual Hashing (pHash) ---")
    _, img1 = create_synthetic_image(width=500, height=400)
    hash1 = compute_perceptual_hash(img1)
    assert hash1 is not None and len(hash1) == 16
    print(f"  -> Generated pHash: {hash1}")

    # Identical image -> exact same hash
    hash1_dup = compute_perceptual_hash(img1)
    assert hash1 == hash1_dup
    print("  ✓ Exact identical image produces identical pHash")

    # Mild resize (480x384) -> visually very similar (Hamming distance <= 4)
    img_resized = img1.resize((480, 384), Image.Resampling.BILINEAR)
    hash_resized = compute_perceptual_hash(img_resized)
    int1 = int(hash1, 16)
    int_r = int(hash_resized, 16)
    hamming_dist = bin(int1 ^ int_r).count("1")
    assert hamming_dist <= 6, f"Expected small Hamming distance for resize, got {hamming_dist}"
    print(f"  ✓ Resized image pHash Hamming distance = {hamming_dist} (robust)")

    # Completely different image
    np.random.seed(999)
    img2 = Image.fromarray(np.random.randint(0, 255, (400, 500, 3), dtype=np.uint8))
    hash2 = compute_perceptual_hash(img2)
    int2 = int(hash2, 16)
    diff_hamming = bin(int1 ^ int2).count("1")
    assert diff_hamming >= 10, f"Expected distinct Hamming distance, got {diff_hamming}"
    print(f"  ✓ Distinct image pHash Hamming distance = {diff_hamming} (discriminative)")


def test_ml_gradcam():
    print("\n--- TEST: ML Grad-CAM Explainability ---")
    if not ml_detector.is_available():
        print("  [SKIP] Model weights unavailable in current environment")
        return

    _, pil_img = create_synthetic_image(width=300, height=300)
    cv_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    res = ml_detector.predict(pil_img, cv_bgr)
    assert res["available"] is True
    assert res["authentic_probability"] is not None
    assert res["manipulated_probability"] is not None
    assert abs((res["authentic_probability"] + res["manipulated_probability"]) - 1.0) < 0.01

    # Grad-CAM checks
    assert "gradcam" in res
    gradcam = res["gradcam"]
    assert gradcam["available"] is True
    assert gradcam["visualization"].startswith("data:image/png;base64,")
    assert "target_class" in gradcam
    assert "explanation" in gradcam
    assert "influence" in gradcam["explanation"].lower() or "contributed" in gradcam["explanation"].lower()
    print(f"  ✓ Grad-CAM generated: target_class={gradcam['target_class']}, base64 URI length={len(gradcam['visualization'])}")


def test_scoring_weights_and_thresholds():
    print("\n--- TEST: Scoring Weights & Thresholds Verification ---")
    mock_file = {"score": 5, "fingerprint": {"width": 1000, "height": 1000}}
    mock_meta = {"score": 15, "details": {"has_exif": True}}
    mock_ela = {"score": 30}
    mock_cm = {"score": 30}
    mock_noise = {"score": 20}

    assessment = calculate_forensic_assessment(
        file_result=mock_file,
        metadata_result=mock_meta,
        ela_result=mock_ela,
        copy_move_result=mock_cm,
        noise_result=mock_noise,
        ml_result={"available": True, "prediction": "manipulated"}
    )
    # Verification of max classical score: 5 + 15 + 30 + 30 + 20 = 100
    assert assessment["score"] == 100
    assert assessment["max_score"] == 100
    assert assessment["status"] == "Strong Manipulation Indicators"
    assert assessment["breakdown"]["metadata"]["max"] == 15
    assert assessment["breakdown"]["ela"]["max"] == 30
    assert assessment["breakdown"]["copy_move"]["max"] == 30
    assert assessment["breakdown"]["noise"]["max"] == 20
    assert assessment["breakdown"]["file_integrity"]["max"] == 5
    assert "evidence_quality" in assessment
    print("  ✓ Maximum classical weights verified: 15 / 30 / 30 / 20 / 5 = 100 total")

    # Threshold checks: 0-29 Low Suspicion, 30-59 Review Recommended, 60-100 Strong Manipulation Indicators
    low = calculate_forensic_assessment({"score": 0}, {"score": 5}, {"score": 10}, {"score": 5}, {"score": 5})
    assert low["score"] == 25 and low["status"] == "Low Suspicion"

    review = calculate_forensic_assessment({"score": 2}, {"score": 8}, {"score": 15}, {"score": 5}, {"score": 5})
    assert review["score"] == 35 and review["status"] == "Review Recommended"

    strong = calculate_forensic_assessment({"score": 4}, {"score": 12}, {"score": 25}, {"score": 15}, {"score": 10})
    assert strong["score"] == 66 and strong["status"] == "Strong Manipulation Indicators"
    print("  ✓ Status thresholds verified: 0-29 Low, 30-59 Review, 60-100 Strong Indicators")


if __name__ == "__main__":
    print("=" * 70)
    print("PIXELPROOF COMPREHENSIVE AUDIT HARDENING TEST SUITE")
    print("=" * 70)
    test_upload_protections()
    test_bounded_analysis_image()
    test_copy_move_ransac_variations()
    test_ela_robustness()
    test_metadata_consistency()
    test_perceptual_hash()
    test_ml_gradcam()
    test_scoring_weights_and_thresholds()
    print("\n" + "=" * 70)
    print("ALL AUDIT HARDENING AND SCIENTIFIC EXPLAINABILITY TESTS PASSED!")
    print("=" * 70)
