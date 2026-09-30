import io
import asyncio
import numpy as np
from PIL import Image, ImageDraw
import cv2
from starlette.datastructures import UploadFile
from fastapi import HTTPException
from app.routes.analysis import analyze_image_endpoint
from app.main import health_check

def test_health():
    print("Testing health check ...")
    res = health_check()
    assert res["status"] == "ok"
    assert res["service"] == "PixelProof Forensics"
    assert "ml_model" in res
    assert res["ml_model"]["model"] == "EfficientNet-B0"
    print("✓ Health check passed!")

def test_normal_jpeg():
    print("\nTesting Normal JPEG ...")
    img = Image.new("RGB", (320, 240), color=(180, 210, 240))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 280, 200], fill=(240, 240, 250), outline=(50, 100, 180), width=2)
    draw.ellipse([100, 80, 220, 160], fill=(255, 200, 100))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    
    upload = UploadFile(file=buf, filename="landscape.jpg", headers={"content-type": "image/jpeg"})
    data = asyncio.run(analyze_image_endpoint(upload))
    
    assert "analysis_id" in data
    assert data["file"]["format"] == "JPEG"
    assert len(data["file"]["sha256"]) == 64
    assert "score" in data["result"]
    assert data["ela"]["visualization"].startswith("data:image/png;base64,")
    assert data["copy_move"]["visualization"].startswith("data:image/png;base64,")
    assert data["noise"]["visualization"].startswith("data:image/png;base64,")
    print(f"✓ Normal JPEG passed! Score: {data['result']['score']}/100, Status: {data['result']['status']}")

def test_png_image():
    print("\nTesting PNG Image ...")
    img = Image.new("RGB", (250, 250), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.polygon([(125, 20), (220, 220), (30, 220)], fill=(37, 99, 235))
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    upload = UploadFile(file=buf, filename="vector_graphic.png", headers={"content-type": "image/png"})
    data = asyncio.run(analyze_image_endpoint(upload))
    
    assert data["file"]["format"] == "PNG"
    print(f"✓ PNG Image passed! Score: {data['result']['score']}/100, Status: {data['result']['status']}")

def test_copy_move_cloning():
    print("\nTesting Controlled Copy-Move Cloned Image ...")
    arr = np.full((400, 600, 3), 245, dtype=np.uint8)
    
    # Generate unique texture patch
    np.random.seed(42)
    patch = np.random.randint(20, 220, (70, 70, 3), dtype=np.uint8)
    cv2.circle(patch, (35, 35), 25, (0, 0, 255), 3)
    cv2.rectangle(patch, (10, 10), (60, 60), (0, 255, 0), 2)
    
    arr[80:150, 100:170] = patch
    arr[80:150, 420:490] = patch
    
    pil_img = Image.fromarray(arr)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    
    upload = UploadFile(file=buf, filename="cloned_stamp.jpg", headers={"content-type": "image/jpeg"})
    data = asyncio.run(analyze_image_endpoint(upload))
    
    print(f"✓ Copy-Move test completed! Copy-Move Score: {data['copy_move']['score']}/30, Status: {data['copy_move']['status']}")

def test_invalid_file():
    print("\nTesting Invalid / Corrupted File Rejection ...")
    corrupt_bytes = b"THIS IS NOT A VALID IMAGE HEADER AT ALL"
    buf = io.BytesIO(corrupt_bytes)
    upload = UploadFile(file=buf, filename="fake.jpg", headers={"content-type": "image/jpeg"})
    try:
        asyncio.run(analyze_image_endpoint(upload))
        assert False, "Expected HTTPException 422"
    except HTTPException as e:
        assert e.status_code == 422
        print(f"✓ Corrupted file properly rejected with HTTP {e.status_code}: {e.detail}")

def test_empty_file():
    print("\nTesting Empty 0-byte File Rejection ...")
    buf = io.BytesIO(b"")
    upload = UploadFile(file=buf, filename="empty.jpg", headers={"content-type": "image/jpeg"})
    try:
        asyncio.run(analyze_image_endpoint(upload))
        assert False, "Expected HTTPException 422"
    except HTTPException as e:
        assert e.status_code == 422
        print(f"✓ Empty file properly rejected with HTTP {e.status_code}: {e.detail}")

if __name__ == "__main__":
    test_health()
    test_normal_jpeg()
    test_png_image()
    test_copy_move_cloning()
    test_invalid_file()
    test_empty_file()
    print("\n==========================================")
    print("ALL 6 FORENSIC PIPELINE TEST SUITES PASSED!")
    print("==========================================")
