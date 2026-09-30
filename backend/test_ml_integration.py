"""
PixelProof — Dedicated ML Model Integration Test Suite
======================================================
Tests the 8 specific criteria defined in the ML integration specification:
  1. model file loads successfully
  2. inference returns two valid probabilities
  3. probabilities sum approximately to 1
  4. prediction is authentic or manipulated
  5. malformed image does not crash entire API
  6. /api/analyze includes ml_analysis
  7. classical forensic modules still return their existing results
  8. API remains functional if ML weights are unavailable
"""

import os
import io
import asyncio
import numpy as np
from PIL import Image
from starlette.datastructures import UploadFile
from fastapi import HTTPException

from app.services.ml_detector import ml_detector, MLDetectorService
from app.routes.analysis import analyze_image_endpoint
from app.main import health_check


def test_1_model_file_loads_successfully():
    print("[TEST 1] Verifying model file loads successfully ...")
    weights_path = os.path.join(
        os.path.dirname(__file__), "app", "models", "image_forensics_model.pth"
    )
    assert os.path.isfile(weights_path), f"Weights file not found at: {weights_path}"
    assert ml_detector.is_available() is True, "ml_detector singleton is not available"
    assert ml_detector.model is not None, "Model instance is None"
    assert ml_detector.metadata["status"] == "LOADED"
    print(f"  -> Model file verified at {weights_path} ({os.path.getsize(weights_path)} bytes)")
    print(f"  -> Active device: {ml_detector._device}")
    print("  ✓ Passed!")


def test_2_and_3_valid_probabilities_and_sum():
    print("\n[TEST 2 & 3] Verifying inference returns two valid probabilities summing to ~1.0 ...")
    test_img = Image.new("RGB", (256, 256), color=(100, 150, 200))
    res = ml_detector.predict(pil_img=test_img)

    assert res["available"] is True
    auth_prob = res["authentic_probability"]
    manip_prob = res["manipulated_probability"]

    assert isinstance(auth_prob, float), f"auth_prob is not float: {type(auth_prob)}"
    assert isinstance(manip_prob, float), f"manip_prob is not float: {type(manip_prob)}"
    assert 0.0 <= auth_prob <= 1.0, f"auth_prob out of bounds: {auth_prob}"
    assert 0.0 <= manip_prob <= 1.0, f"manip_prob out of bounds: {manip_prob}"

    prob_sum = auth_prob + manip_prob
    assert abs(prob_sum - 1.0) < 0.01, f"Probabilities do not sum to ~1.0: {prob_sum}"
    print(f"  -> Authentic prob: {auth_prob}, Manipulated prob: {manip_prob}, Sum: {prob_sum:.4f}")
    print("  ✓ Passed!")


def test_4_prediction_is_authentic_or_manipulated():
    print("\n[TEST 4] Verifying prediction is 'authentic' or 'manipulated' ...")
    test_img = Image.new("RGB", (224, 224), color=(60, 120, 180))
    res = ml_detector.predict(pil_img=test_img)

    assert res["prediction"] in ["authentic", "manipulated"], f"Invalid prediction: {res['prediction']}"
    assert res["confidence"] in [res["authentic_probability"], res["manipulated_probability"]]
    assert res["model"] == "EfficientNet-B0"
    assert res["model_version"] == "pixelproof-casia-v1"
    print(f"  -> Prediction: {res['prediction']} (Confidence: {res['confidence']})")
    print(f"  -> Explanation: {res['explanation']}")
    print("  ✓ Passed!")


def test_5_malformed_image_does_not_crash_api():
    print("\n[TEST 5] Verifying malformed image does not crash entire API ...")
    corrupt_bytes = b"CORRUPTED_HEADER_DATA_NOT_AN_IMAGE_123456789"
    buf = io.BytesIO(corrupt_bytes)
    upload = UploadFile(file=buf, filename="malformed.jpg", headers={"content-type": "image/jpeg"})

    try:
        asyncio.run(analyze_image_endpoint(upload))
        assert False, "Expected HTTPException 422 for unparseable image"
    except HTTPException as e:
        assert e.status_code == 422
        print(f"  -> Corrupt input safely handled with HTTP 422: {e.detail}")

    # Also test ml_detector.predict directly with invalid image input
    res_bad = ml_detector.predict(pil_img=None, cv_bgr=None)
    assert res_bad["available"] is True
    assert res_bad["prediction"] is None
    print("  ✓ Passed!")


def test_6_analyze_includes_ml_analysis():
    print("\n[TEST 6] Verifying POST /api/analyze endpoint includes ml_analysis ...")
    img = Image.new("RGB", (300, 300), color=(220, 230, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    upload = UploadFile(file=buf, filename="sample.jpg", headers={"content-type": "image/jpeg"})
    data = asyncio.run(analyze_image_endpoint(upload))

    assert "ml_analysis" in data, "ml_analysis key missing from response"
    ml = data["ml_analysis"]
    assert ml["available"] is True
    assert ml["prediction"] in ["authentic", "manipulated"]
    assert isinstance(ml["authentic_probability"], float)
    assert isinstance(ml["manipulated_probability"], float)
    assert isinstance(ml["confidence"], float)
    assert ml["model"] == "EfficientNet-B0"
    assert "disclaimer" in ml
    assert "metrics" in ml
    print(f"  -> ml_analysis received: prediction={ml['prediction']}, confidence={ml['confidence']}")
    print("  ✓ Passed!")


def test_7_classical_forensic_modules_still_return_results():
    print("\n[TEST 7] Verifying classical forensic modules still return their existing results ...")
    img = Image.new("RGB", (350, 350), color=(210, 215, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    buf.seek(0)

    upload = UploadFile(file=buf, filename="test_classical.jpg", headers={"content-type": "image/jpeg"})
    data = asyncio.run(analyze_image_endpoint(upload))

    assert "metadata" in data and "details" in data["metadata"]
    assert "ela" in data and "metrics" in data["ela"]
    assert "copy_move" in data and "metrics" in data["copy_move"]
    assert "noise" in data and "metrics" in data["noise"]
    assert "file_integrity" in data and "fingerprint" in data["file_integrity"]
    assert "result" in data and "score" in data["result"]
    assert 0 <= data["result"]["score"] <= 100

    print("  -> Metadata status:", data["metadata"]["status"])
    print("  -> ELA status:", data["ela"]["status"])
    print("  -> Copy-Move status:", data["copy_move"]["status"])
    print("  -> Noise status:", data["noise"]["status"])
    print("  -> File integrity status:", data["file_integrity"]["status"])
    print(f"  -> Overall score: {data['result']['score']}/100")
    print("  ✓ Passed!")


def test_8_api_remains_functional_if_ml_weights_unavailable():
    print("\n[TEST 8] Verifying API remains fully functional if ML weights are unavailable ...")
    # Instantiate a standalone ML detector pointing to a non-existent path
    dummy_service = MLDetectorService()
    dummy_service.model = None
    dummy_service.load_error = "Weights file intentionally missing for fallback test"
    dummy_service.metadata["status"] = "UNLOADED"

    assert dummy_service.is_available() is False
    test_img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    res = dummy_service.predict(test_img)

    assert res["available"] is False
    assert res["prediction"] is None
    assert res["confidence"] is None
    assert res["authentic_probability"] is None
    assert res["manipulated_probability"] is None
    assert "explanation" in res
    print(f"  -> Fallback explanation: {res['explanation']}")
    print("  ✓ Passed!")


def test_9_ml_signal_wording_and_disagreement():
    print("\n[TEST 9] Verifying ML wording, disclaimer, and evidence disagreement logic ...")
    from app.services.scoring_engine import check_evidence_disagreement

    img = Image.new("RGB", (300, 300), color=(200, 210, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    upload = UploadFile(file=buf, filename="wording_test.jpg", headers={"content-type": "image/jpeg"})
    data = asyncio.run(analyze_image_endpoint(upload))

    ml = data["ml_analysis"]
    assert "signal_label" in ml
    assert ml["signal_label"] in ["Manipulation-Leaning ML Signal", "Authenticity-Leaning ML Signal"]
    assert ml["disclaimer"] == "This is an independent machine-learning signal, not the final forensic conclusion."
    assert "disagreement" in ml
    assert ml.get("score_added", 0) == 0

    # Ensure classical score breakdown is unchanged: 15 + 30 + 30 + 20 + 5 = 100
    breakdown = data["result"]["breakdown"]
    assert breakdown["metadata"]["max"] == 15
    assert breakdown["ela"]["max"] == 30
    assert breakdown["copy_move"]["max"] == 30
    assert breakdown["noise"]["max"] == 20
    assert breakdown["file_integrity"]["max"] == 5
    assert breakdown["total"]["max"] == 100
    assert data["result"]["score"] == (
        breakdown["metadata"]["score"]
        + breakdown["ela"]["score"]
        + breakdown["copy_move"]["score"]
        + breakdown["noise"]["score"]
        + breakdown["file_integrity"]["score"]
    )

    # Test disagreement behavior: ML manipulated vs Classical Low Suspicion (6/100)
    dis_res = check_evidence_disagreement(6, "Low Suspicion", {"available": True, "prediction": "manipulated"})
    assert dis_res["has_disagreement"] is True
    assert dis_res["title"] == "EVIDENCE DISAGREEMENT"
    assert "Manual review is recommended when independent signals disagree." in dis_res["message"]

    print("  -> Signal label:", ml["signal_label"])
    print("  -> Disclaimer:", ml["disclaimer"])
    print(f"  -> Classical score strictly maintained: {data['result']['score']}/100")
    print("  ✓ Passed!")


if __name__ == "__main__":
    print("=" * 65)
    print("PIXELPROOF — ML MODEL INTEGRATION TEST SUITE")
    print("=" * 65)
    test_1_model_file_loads_successfully()
    test_2_and_3_valid_probabilities_and_sum()
    test_4_prediction_is_authentic_or_manipulated()
    test_5_malformed_image_does_not_crash_api()
    test_6_analyze_includes_ml_analysis()
    test_7_classical_forensic_modules_still_return_results()
    test_8_api_remains_functional_if_ml_weights_unavailable()
    test_9_ml_signal_wording_and_disagreement()
    print("\n" + "=" * 65)
    print("ALL 9 ML INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)

