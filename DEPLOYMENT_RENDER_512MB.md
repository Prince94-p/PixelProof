# Render 512 MB Free-Tier Deployment Configuration

This document specifies the exact production deployment configuration required to run PixelProof's backend on Render's 512 MB RAM instance without exceeding memory limits.

## 1. Service Specifications

| Setting | Value |
| :--- | :--- |
| **Environment** | Python 3 |
| **Python Version** | `3.11.9` (pinned via `.python-version` and `backend/.python-version`) |
| **Root Directory** | `backend` |
| **Instance Type** | Free (512 MB RAM, 0.5 CPU) |
| **Auto-Deploy** | Yes (on push to `main`) |

## 2. Build Command

```bash
pip install --upgrade pip && pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r requirements.txt && mkdir -p app/models && if [ ! -f app/models/image_forensics_model.pth ]; then curl -L -o app/models/image_forensics_model.pth https://github.com/Prince94-p/PixelProof/releases/download/v1.0.0/image_forensics_model.pth; fi
```

### Why this build command is required:
- `--index-url https://download.pytorch.org/whl/cpu`: Installs official PyTorch CPU-only wheels instead of default PyPI wheels that bundle ~2.5 GB of NVIDIA CUDA 12 packages.
- `--no-cache-dir`: Keeps pip cache from filling disk during container build.
- `curl ... image_forensics_model.pth`: Safely downloads the trained EfficientNet-B0 weights directly into `app/models/` without checking large binary files into Git.

## 3. Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

> **CRITICAL:** Do NOT increase `--workers` above `1`. Multiple Uvicorn workers duplicate PyTorch and model weights in RAM, exceeding 512 MB.

## 4. Runtime Memory Safeguards

1. **Model Singleton:** EfficientNet-B0 is instantiated exactly once at process startup. Deserialized `state_dict` objects are discarded immediately with `del` and `gc.collect()`.
2. **CPU Thread Limiting:** `torch.set_num_threads(1)` limits OpenMP thread stack memory.
3. **Inference Mode:** Classification executes under `torch.inference_mode()` with immediate deletion of intermediate logits, probabilities, and normalized tensors.
4. **Grad-CAM Memory Safety:** Hooks are tracked within strict `try ... finally` blocks, gradients are cleared with `model.zero_grad(set_to_none=True)`, and overlays are computed at thumbnail scale (640px) to prevent 45 MB full-canvas array allocations.
5. **Early Bounding:** Images exceeding 2048px are downscaled at the PIL stage before NumPy or OpenCV BGR/Grayscale matrices are instantiated.
6. **In-Process Concurrency Guard:** `ANALYSIS_SEMAPHORE = asyncio.Semaphore(1)` serializes CPU-intensive analyses to ensure active memory never doubles.
7. **End-of-Request Cleanup:** `_execute_pipeline` runs inside a `try ... finally` block that deletes all uncompressed pixel matrices and calls `gc.collect()`.

## 5. Measured Memory Profile

- **Baseline RSS (Model Loaded, CPU):** ~140–160 MB
- **Peak RSS during 2000px Image Analysis:** ~310–350 MB
- **Safety Margin:** ~160 MB headroom within Render's 512 MB threshold.
