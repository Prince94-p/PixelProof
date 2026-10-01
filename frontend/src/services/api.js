/**
 * PixelProof API Client
 * Interacts with the backend digital forensic pipeline.
 */

// Centralized API Base URL:
// Reads from Vite environment variable VITE_API_BASE_URL in production (e.g. https://pixelproof-74zd.onrender.com)
// with fallback to local development server (http://localhost:8000).
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000';
const BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${BASE_URL}/api/health`);
    if (!res.ok) throw new Error(`Health check failed with status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('API health check error:', err);
    return { status: 'offline', error: err.message };
  }
}

export async function analyzeImageFile(file) {
  if (!file) {
    throw new Error('Please select an image file to analyze.');
  }

  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    let errorDetail = 'Analysis failed.';
    try {
      const errorJson = await res.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch {
      errorDetail = `Server responded with status code ${res.status}`;
    }
    throw new Error(errorDetail);
  }

  return await res.json();
}
