from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analysis import router as analysis_router

app = FastAPI(
    title="PixelProof Digital Forensic Analysis API",
    description="Scientific image authenticity and manipulation detection API",
    version="1.0.0"
)

# Explicit allowed origins including production domain and local development
ALLOWED_ORIGINS = [
    "https://pixelproof-1.onrender.com",
    "https://curly-pixel-proof-lab.base44.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://.*\.onrender\.com|https?://.*\.base44\.app|https?://localhost(:\d+)?|https?://127\.0\.0\.1(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(analysis_router)

@app.get("/api/health")
def health_check():
    """Service health check endpoint with ML model status."""
    from app.services.ml_detector import ml_detector
    return {
        "status": "ok",
        "service": "PixelProof Forensics",
        "ml_model": {
            "available": ml_detector.is_available(),
            "model": "EfficientNet-B0",
            "model_version": "pixelproof-casia-v1"
        }
    }
