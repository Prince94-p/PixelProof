import io
import json
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import cv2
from starlette.datastructures import UploadFile

from app.routes.analysis import analyze_image_endpoint
from app.services.copy_move_detector import detect_copy_move
from app.services.ela_analyzer import analyze_ela
from app.services.noise_analyzer import analyze_noise_consistency
from app.services.ml_detector import ml_detector

def run_controlled_forensics():
    results = {}
    print("=" * 70)
    print("PIXELPROOF COMPREHENSIVE CONTROLLED FORENSIC VALIDATION SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST 1: Authentic Clean JPEG (No Tampering)
    # -------------------------------------------------------------
    print("\n[TEST 1] Authentic Clean JPEG ...")
    np.random.seed(101)
    base_img = Image.new("RGB", (640, 480), color=(140, 180, 220))
    draw = ImageDraw.Draw(base_img)
    # Draw natural gradient and diverse distinct natural elements without repetition
    for y in range(480):
        shade = int(140 + 80 * (y / 480))
        draw.line([(0, y), (640, y)], fill=(shade, shade + 15, shade + 35))
    # Mountain peak left
    draw.polygon([(0, 480), (160, 240), (340, 480)], fill=(55, 80, 65))
    # Rolling foothill right with different aspect/geometry
    draw.polygon([(280, 480), (490, 310), (640, 480)], fill=(85, 115, 75))
    # Sun
    draw.ellipse([(470, 70), (550, 150)], fill=(255, 225, 120))
    # Lake in foreground
    draw.polygon([(100, 480), (280, 410), (460, 480)], fill=(70, 120, 160))
    
    buf_clean = io.BytesIO()
    base_img.save(buf_clean, format="JPEG", quality=92)
    clean_bytes = buf_clean.getvalue()
    
    upload = UploadFile(file=io.BytesIO(clean_bytes), filename="authentic_landscape.jpg", headers={"content-type": "image/jpeg"})
    res_clean = asyncio.run(analyze_image_endpoint(upload))
    
    results["authentic_clean_jpeg"] = {
        "status": res_clean["result"]["status"],
        "score": res_clean["result"]["score"],
        "ela_score": res_clean["ela"]["score"],
        "ela_mean_diff": res_clean["ela"]["metrics"]["global_mean_error"],
        "copy_move_score": res_clean["copy_move"]["score"],
        "copy_move_matches": res_clean["copy_move"]["metrics"]["verified_matches"],
        "noise_score": res_clean["noise"]["score"],
        "ml_available": res_clean["ml_analysis"]["available"],
        "ml_score_added": res_clean["ml_analysis"].get("score_added", 0),
    }
    print(f"  -> Score: {res_clean['result']['score']}/100 | ELA: {res_clean['ela']['score']}/30 | CopyMove: {res_clean['copy_move']['score']}/30 | Noise: {res_clean['noise']['score']}/20")
    print(f"  -> ML Available: {res_clean['ml_analysis']['available']} | Status: {res_clean['result']['status']}")
    assert res_clean["result"]["score"] < 30, f"Expected clean JPEG score < 30, got {res_clean['result']['score']}"
    assert isinstance(res_clean["ml_analysis"]["available"], bool)

    # -------------------------------------------------------------
    # TEST 2: Exact Copied Patch (Copy-Move Forgery)
    # -------------------------------------------------------------
    print("\n[TEST 2] Exact Copied Patch (Cloning) ...")
    canvas = np.full((500, 700, 3), 235, dtype=np.uint8)
    # Add subtle background texture
    noise_bg = np.random.normal(0, 3, canvas.shape).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise_bg, 0, 255).astype(np.uint8)
    
    # Create distinct geometric patch
    patch = np.zeros((80, 80, 3), dtype=np.uint8)
    cv2.rectangle(patch, (5, 5), (75, 75), (200, 50, 40), -1)
    cv2.circle(patch, (40, 40), 25, (40, 180, 220), -1)
    cv2.putText(patch, "STAMP", (12, 46), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    
    # Place patch in two separated locations
    canvas[100:180, 100:180] = patch
    canvas[100:180, 480:560] = patch
    
    buf_exact = io.BytesIO()
    Image.fromarray(canvas).save(buf_exact, format="JPEG", quality=94)
    exact_bytes = buf_exact.getvalue()
    
    upload = UploadFile(file=io.BytesIO(exact_bytes), filename="exact_cloned_patch.jpg", headers={"content-type": "image/jpeg"})
    res_exact = asyncio.run(analyze_image_endpoint(upload))
    
    results["exact_copied_patch"] = {
        "status": res_exact["result"]["status"],
        "score": res_exact["result"]["score"],
        "copy_move_score": res_exact["copy_move"]["score"],
        "candidate_matches": res_exact["copy_move"]["metrics"]["candidate_matches"],
        "verified_matches": res_exact["copy_move"]["metrics"]["verified_matches"],
        "coherent_clusters": res_exact["copy_move"]["metrics"]["coherent_clusters"],
        "dominant_cluster_size": res_exact["copy_move"]["metrics"]["dominant_cluster_size"],
        "geometric_cluster_evidence": res_exact["copy_move"]["metrics"]["geometric_cluster_evidence"],
    }
    print(f"  -> Candidate Matches: {res_exact['copy_move']['metrics']['candidate_matches']}")
    print(f"  -> Verified Matches: {res_exact['copy_move']['metrics']['verified_matches']}")
    print(f"  -> Coherent Clusters: {res_exact['copy_move']['metrics']['coherent_clusters']}")
    print(f"  -> Geometric Cluster Evidence: {res_exact['copy_move']['metrics']['geometric_cluster_evidence']}")
    print(f"  -> Copy-Move Score: {res_exact['copy_move']['score']}/30")
    assert res_exact["copy_move"]["score"] >= 15, "Expected copy-move score >= 15 for exact cloned patch"
    assert res_exact["copy_move"]["metrics"]["verified_matches"] >= 4

    # -------------------------------------------------------------
    # TEST 3: Textured Copied Patch (Rich Texture Cloning)
    # -------------------------------------------------------------
    print("\n[TEST 3] Textured Copied Patch ...")
    canvas_tex = np.full((500, 700, 3), 220, dtype=np.uint8)
    np.random.seed(42)
    # Rich high-frequency texture
    rich_patch = np.random.randint(40, 210, (90, 90, 3), dtype=np.uint8)
    rich_patch = cv2.GaussianBlur(rich_patch, (3, 3), 1.0)
    for i in range(5):
        cv2.line(rich_patch, (i * 18, 0), (90, 90 - i * 18), (255, 0, 100), 2)
        cv2.circle(rich_patch, (20 + i * 12, 70 - i * 8), 6, (0, 220, 255), -1)
        
    canvas_tex[120:210, 80:170] = rich_patch
    canvas_tex[280:370, 480:570] = rich_patch
    
    buf_tex = io.BytesIO()
    Image.fromarray(canvas_tex).save(buf_tex, format="JPEG", quality=95)
    
    upload = UploadFile(file=io.BytesIO(buf_tex.getvalue()), filename="textured_cloned_patch.jpg", headers={"content-type": "image/jpeg"})
    res_tex = asyncio.run(analyze_image_endpoint(upload))
    
    results["textured_copied_patch"] = {
        "status": res_tex["result"]["status"],
        "score": res_tex["result"]["score"],
        "copy_move_score": res_tex["copy_move"]["score"],
        "candidate_matches": res_tex["copy_move"]["metrics"]["candidate_matches"],
        "verified_matches": res_tex["copy_move"]["metrics"]["verified_matches"],
        "coherent_clusters": res_tex["copy_move"]["metrics"]["coherent_clusters"],
        "geometric_cluster_evidence": res_tex["copy_move"]["metrics"]["geometric_cluster_evidence"],
    }
    print(f"  -> Candidate Matches: {res_tex['copy_move']['metrics']['candidate_matches']}")
    print(f"  -> Verified Matches: {res_tex['copy_move']['metrics']['verified_matches']}")
    print(f"  -> Coherent Clusters: {res_tex['copy_move']['metrics']['coherent_clusters']}")
    print(f"  -> Geometric Cluster Evidence: {res_tex['copy_move']['metrics']['geometric_cluster_evidence']}")
    print(f"  -> Copy-Move Score: {res_tex['copy_move']['score']}/30")
    assert res_tex["copy_move"]["score"] >= 15

    # -------------------------------------------------------------
    # TEST 4: Repeated Natural Texture (Periodic Grid / Bricks)
    # -------------------------------------------------------------
    print("\n[TEST 4] Repeated Natural Texture (Grid / Periodic Tiles) ...")
    canvas_rep = np.full((500, 700, 3), 240, dtype=np.uint8)
    # Draw repeating window grid / tile pattern across entire image
    for r in range(40, 460, 50):
        for c in range(40, 660, 50):
            cv2.rectangle(canvas_rep, (c, r), (c + 35, r + 35), (70, 110, 150), 2)
            cv2.circle(canvas_rep, (c + 17, r + 17), 5, (180, 80, 50), -1)
            
    buf_rep = io.BytesIO()
    Image.fromarray(canvas_rep).save(buf_rep, format="JPEG", quality=90)
    
    upload = UploadFile(file=io.BytesIO(buf_rep.getvalue()), filename="repeated_texture_grid.jpg", headers={"content-type": "image/jpeg"})
    res_rep = asyncio.run(analyze_image_endpoint(upload))
    
    results["repeated_natural_texture"] = {
        "status": res_rep["result"]["status"],
        "score": res_rep["result"]["score"],
        "copy_move_score": res_rep["copy_move"]["score"],
        "copy_move_status": res_rep["copy_move"]["status"],
        "candidate_matches": res_rep["copy_move"]["metrics"]["candidate_matches"],
        "verified_matches": res_rep["copy_move"]["metrics"]["verified_matches"],
        "coherent_clusters": res_rep["copy_move"]["metrics"]["coherent_clusters"],
        "geometric_cluster_evidence": res_rep["copy_move"]["metrics"]["geometric_cluster_evidence"],
    }
    print(f"  -> Candidate Matches: {res_rep['copy_move']['metrics']['candidate_matches']}")
    print(f"  -> Verified Matches: {res_rep['copy_move']['metrics']['verified_matches']}")
    print(f"  -> Coherent Clusters: {res_rep['copy_move']['metrics']['coherent_clusters']}")
    print(f"  -> Copy-Move Status: {res_rep['copy_move']['status']}")
    print(f"  -> Copy-Move Score: {res_rep['copy_move']['score']}/30 (Should not trigger localized forgery false positive)")
    # Should not produce full localized forgery score 30
    assert res_rep["copy_move"]["score"] <= 12, f"Expected periodic grid score <= 12, got {res_rep['copy_move']['score']}"

    # -------------------------------------------------------------
    # TEST 5: Recompressed Clean JPEG (Saved Twice)
    # -------------------------------------------------------------
    print("\n[TEST 5] Recompressed Clean JPEG ...")
    # Clean image saved once at Q=92, then re-saved at Q=85 without splicing
    img_recomp = Image.open(io.BytesIO(clean_bytes))
    buf_recomp = io.BytesIO()
    img_recomp.save(buf_recomp, format="JPEG", quality=85)
    
    upload = UploadFile(file=io.BytesIO(buf_recomp.getvalue()), filename="recompressed_clean.jpg", headers={"content-type": "image/jpeg"})
    res_recomp = asyncio.run(analyze_image_endpoint(upload))
    
    results["recompressed_clean_jpeg"] = {
        "status": res_recomp["result"]["status"],
        "score": res_recomp["result"]["score"],
        "ela_score": res_recomp["ela"]["score"],
        "ela_status": res_recomp["ela"]["status"],
        "ela_max_diff": res_recomp["ela"]["metrics"]["max_pixel_diff"],
        "noise_score": res_recomp["noise"]["score"],
    }
    print(f"  -> Recompressed Clean Score: {res_recomp['result']['score']}/100 | ELA: {res_recomp['ela']['score']}/30 | Status: {res_recomp['result']['status']}")
    assert res_recomp["result"]["score"] < 30, f"Expected uniform recompressed score < 30, got {res_recomp['result']['score']}"

    # -------------------------------------------------------------
    # TEST 6: Lossless PNG Image (No JPEG DCT Grid)
    # -------------------------------------------------------------
    print("\n[TEST 6] Lossless PNG Graphic ...")
    png_img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    draw_png = ImageDraw.Draw(png_img)
    draw_png.rectangle([50, 50, 350, 350], fill=(37, 99, 235), outline=(15, 23, 42), width=4)
    draw_png.text((100, 180), "PIXELPROOF LABS", fill=(255, 255, 255))
    
    buf_png = io.BytesIO()
    png_img.save(buf_png, format="PNG")
    
    upload = UploadFile(file=io.BytesIO(buf_png.getvalue()), filename="vector_diagram.png", headers={"content-type": "image/png"})
    res_png = asyncio.run(analyze_image_endpoint(upload))
    
    results["png_image"] = {
        "format": res_png["file"]["format"],
        "status": res_png["result"]["status"],
        "score": res_png["result"]["score"],
        "ela_status": res_png["ela"]["status"],
        "ela_score": res_png["ela"]["score"],
        "noise_score": res_png["noise"]["score"],
    }
    print(f"  -> Format: {res_png['file']['format']} | Score: {res_png['result']['score']}/100 | ELA Status: {res_png['ela']['status']}")
    assert res_png["file"]["format"] == "PNG"
    assert res_png["result"]["score"] < 30

    # -------------------------------------------------------------
    # TEST 7: Localized Edited / Spliced Image
    # -------------------------------------------------------------
    print("\n[TEST 7] Localized Edited / Spliced Image (Composite) ...")
    # Create realistic base image with texture and natural camera sensor noise floor
    np.random.seed(42)
    base_tex = np.zeros((480, 640, 3), dtype=np.uint8)
    for y in range(480):
        base_tex[y, :] = [int(120 + 70 * (y / 480)), int(140 + 50 * (y / 480)), int(160 + 40 * (y / 480))]
    # Add natural camera sensor noise
    cam_noise = np.random.normal(0, 3.5, base_tex.shape).astype(np.int16)
    base_tex = np.clip(base_tex.astype(np.int16) + cam_noise, 0, 255).astype(np.uint8)
    
    # Save base image at low quality (Q=65) to establish prior JPEG compression history
    buf_low = io.BytesIO()
    Image.fromarray(base_tex).save(buf_low, format="JPEG", quality=65)
    base_spliced = np.array(Image.open(buf_low))
    
    # Create foreign spliced patch: uncompressed, high-contrast texture with distinct noise profile
    patch_spliced = np.zeros((160, 220, 3), dtype=np.uint8)
    for r in range(160):
        for c in range(220):
            patch_spliced[r, c] = [int(50 + 150 * (r / 160)), int(220 - 160 * (c / 220)), int(80 + (r * c) % 150)]
    cv2.putText(patch_spliced, "SPLICED OBJECT", (15, 85), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)
    # Add disparate sensor noise to spliced patch (sigma=14 vs baseline 3.5)
    foreign_noise = np.random.normal(0, 14.0, patch_spliced.shape).astype(np.int16)
    patch_spliced = np.clip(patch_spliced.astype(np.int16) + foreign_noise, 0, 255).astype(np.uint8)
    
    # Insert spliced patch into canvas
    base_spliced[140:300, 200:420] = patch_spliced
    
    # Save composite at high quality (Q=95)
    buf_spliced = io.BytesIO()
    Image.fromarray(base_spliced).save(buf_spliced, format="JPEG", quality=95)
    
    upload = UploadFile(file=io.BytesIO(buf_spliced.getvalue()), filename="spliced_composite.jpg", headers={"content-type": "image/jpeg"})
    res_spliced = asyncio.run(analyze_image_endpoint(upload))
    
    results["localized_spliced_image"] = {
        "status": res_spliced["result"]["status"],
        "score": res_spliced["result"]["score"],
        "ela_score": res_spliced["ela"]["score"],
        "ela_status": res_spliced["ela"]["status"],
        "noise_score": res_spliced["noise"]["score"],
        "noise_status": res_spliced["noise"]["status"],
    }
    print(f"  -> Score: {res_spliced['result']['score']}/100 | ELA: {res_spliced['ela']['score']}/30 ({res_spliced['ela']['status']}) | Noise: {res_spliced['noise']['score']}/20 ({res_spliced['noise']['status']})")
    print(f"  -> ELA Metrics: {res_spliced['ela']['metrics']}")
    print(f"  -> Noise Metrics: {res_spliced['noise']['metrics']}")
    assert res_spliced["result"]["score"] >= 30, f"Expected spliced image score >= 30, got {res_spliced['result']['score']}"

    # -------------------------------------------------------------
    # TEST 8: ML Detector Service Fallback & Metadata Protocol
    # -------------------------------------------------------------
    print("\n[TEST 8] ML Detector Service Contract & Fallback ...")
    meta = ml_detector.get_metadata()
    pred = ml_detector.predict(pil_img=base_img)
    
    results["ml_detector_contract"] = {
        "model_loaded": ml_detector.is_available(),
        "prediction_available": pred["available"],
        "prediction": pred["prediction"],
        "confidence": pred["confidence"],
        "metadata_keys": list(meta.keys()),
        "explanation": pred["explanation"],
    }
    print(f"  -> Model Loaded: {ml_detector.is_available()}")
    print(f"  -> Prediction Available: {pred['available']}")
    print(f"  -> Explanation: {pred['explanation']}")
    if ml_detector.is_available():
        assert pred["available"] is True
        assert pred["prediction"] in ["authentic", "manipulated"]
        assert pred["confidence"] is not None and 0.0 <= pred["confidence"] <= 1.0
        assert meta["status"] == "LOADED"
        assert meta["model_hash_sha256"] is not None
    else:
        assert pred["available"] is False
        assert pred["prediction"] is None
        assert pred["confidence"] is None
        assert meta["status"] in ["UNLOADED", "NOT_FOUND", "DEPENDENCY_MISSING"]
    assert "metrics" in meta or "test_accuracy" in meta

    print("\n" + "=" * 70)
    print("ALL 8 CONTROLLED VALIDATION EXPERIMENTS PASSED SUCCESSFULLY!")
    print("=" * 70)
    return results

if __name__ == "__main__":
    res = run_controlled_forensics()
    with open("controlled_forensics_results.json", "w") as f:
        json.dump(res, f, indent=2)
    print("Results saved to controlled_forensics_results.json")
