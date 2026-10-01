import io
import asyncio
import unittest
from PIL import Image, ImageDraw
from starlette.datastructures import UploadFile

from app.services.ml_detector import ml_detector
from app.routes.analysis import analyze_image_endpoint, ANALYSIS_SEMAPHORE, _execute_pipeline


class TestMemoryAndConcurrency(unittest.TestCase):
    """
    Automated regression tests verifying low-memory protections,
    model singleton behavior, concurrency guards, and API compatibility.
    """

    def setUp(self):
        # Generate standard test image in memory
        img = Image.new("RGB", (320, 240), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 100, 100], fill=(220, 50, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        self.image_bytes = buf.getvalue()

    def test_model_singleton_behavior(self):
        """Verifies that the EfficientNet-B0 instance is a singleton and not re-created."""
        self.assertTrue(ml_detector.is_available(), "ML model should be loaded and available")
        model_instance_1 = ml_detector.model
        # Execute prediction
        pil_img = Image.open(io.BytesIO(self.image_bytes))
        ml_detector.predict(pil_img)
        model_instance_2 = ml_detector.model
        self.assertIs(model_instance_1, model_instance_2, "ML model instance must be a singleton across calls")

    def test_repeated_analyses_stability(self):
        """Verifies repeated analyses succeed without error or state corruption."""
        for i in range(3):
            upload = UploadFile(
                file=io.BytesIO(self.image_bytes),
                filename=f"test_repeat_{i}.jpg",
                headers={"content-type": "image/jpeg"}
            )
            res = asyncio.run(analyze_image_endpoint(upload))
            self.assertIn("result", res)
            self.assertIn("score", res["result"])
            self.assertIn("ml_analysis", res)
            self.assertEqual(res["ml_analysis"]["score_added"], 0)

    def test_gradcam_graceful_degradation_on_failure(self):
        """Verifies that Grad-CAM failure does not crash the overall ML prediction or forensic analysis."""
        original_gen = ml_detector.generate_gradcam
        try:
            # Force generate_gradcam to simulate an out-of-memory or hook error
            def mock_failing_gradcam(*args, **kwargs):
                return {
                    "available": False,
                    "target_class": None,
                    "visualization": None,
                    "explanation": "Grad-CAM influence map generation was skipped for memory safety: Simulated OOM"
                }

            ml_detector.generate_gradcam = mock_failing_gradcam
            pil_img = Image.open(io.BytesIO(self.image_bytes))
            ml_res = ml_detector.predict(pil_img)

            self.assertTrue(ml_res["available"], "ML prediction must remain available even if Grad-CAM degrades")
            self.assertIsNotNone(ml_res["prediction"])
            self.assertFalse(ml_res["gradcam"]["available"], "Grad-CAM should report unavailable")
            self.assertIn("memory safety", ml_res["gradcam"]["explanation"])
        finally:
            ml_detector.generate_gradcam = original_gen

    def test_concurrency_semaphore_configured(self):
        """Verifies that ANALYSIS_SEMAPHORE limits concurrent analyses to 1 on 512 MB instances."""
        self.assertEqual(ANALYSIS_SEMAPHORE._value, 1, "Concurrency semaphore must be initialized to 1")

    def test_api_compatibility_schema(self):
        """Verifies that all required top-level forensic API keys are strictly preserved."""
        upload = UploadFile(
            file=io.BytesIO(self.image_bytes),
            filename="schema_test.jpg",
            headers={"content-type": "image/jpeg"}
        )
        res = asyncio.run(analyze_image_endpoint(upload))

        expected_keys = [
            "analysis_id",
            "file",
            "analysis_image",
            "result",
            "metadata",
            "ela",
            "copy_move",
            "noise",
            "file_integrity",
            "ml_analysis",
            "evidence",
            "original_preview"
        ]
        for k in expected_keys:
            self.assertIn(k, res, f"Missing required top-level API key: {k}")

        # Verify classical scoring invariants
        self.assertEqual(res["result"]["max_score"], 100)
        self.assertEqual(res["ml_analysis"]["score_added"], 0)
        self.assertEqual(res["metadata"]["max_score"], 15)
        self.assertEqual(res["ela"]["max_score"], 30)
        self.assertEqual(res["copy_move"]["max_score"], 30)
        self.assertEqual(res["noise"]["max_score"], 20)
        self.assertEqual(res["file_integrity"]["max_score"], 5)


if __name__ == "__main__":
    unittest.main()
