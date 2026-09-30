import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import LoadingAnalysis from '../components/LoadingAnalysis';
import { analyzeImageFile } from '../services/api';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function Analyze({ onAnalysisComplete }) {
  const [isLoading, setIsLoading] = useState(false);
  const [currentFile, setCurrentFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleStartAnalysis = async (file) => {
    setIsLoading(true);
    setErrorMsg(null);
    setCurrentFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);

    try {
      const data = await analyzeImageFile(file);
      setIsLoading(false);
      onAnalysisComplete(data);
    } catch (err) {
      console.error('Forensic analysis error:', err);
      setIsLoading(false);
      setErrorMsg(err.message || 'Analysis could not be completed. Please ensure backend service is running.');
    }
  };

  const handleRetry = () => {
    setErrorMsg(null);
    setIsLoading(false);
  };

  return (
    <div style={{
      backgroundColor: '#F7F9FC',
      minHeight: 'calc(100vh - 70px)',
      padding: '48px 0 80px 0'
    }}>
      <div className="container">
        {!isLoading && (
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <h1 style={{
              fontSize: '36px',
              fontWeight: 800,
              color: '#0F172A',
              letterSpacing: '-0.02em',
              marginBottom: '10px'
            }}>
              Analyze an Image
            </h1>
            <p style={{
              fontSize: '16px',
              color: '#64748B',
              maxWidth: '560px',
              margin: '0 auto'
            }}>
              Upload an image to run multiple independent digital-forensic checks and receive an explainable tampering report.
            </p>
          </div>
        )}

        {/* Loading State or Upload Zone */}
        {isLoading ? (
          <LoadingAnalysis
            previewUrl={previewUrl}
            filename={currentFile?.name || 'Uploaded Image'}
          />
        ) : (
          <>
            {errorMsg && (
              <div style={{
                maxWidth: '840px',
                margin: '0 auto 24px auto',
                backgroundColor: '#FEF2F2',
                border: '1px solid #FECACA',
                borderRadius: '10px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '16px'
              }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <AlertCircle size={20} style={{ color: '#DC2626', flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#DC2626', marginBottom: '4px' }}>
                      Analysis Request Failed
                    </h4>
                    <p style={{ fontSize: '14px', color: '#991B1B', margin: 0 }}>
                      {errorMsg}
                    </p>
                  </div>
                </div>

                <button
                  onClick={handleRetry}
                  className="btn-secondary"
                  style={{
                    padding: '8px 14px',
                    fontSize: '13px',
                    flexShrink: 0
                  }}
                >
                  <RefreshCw size={14} />
                  <span>Dismiss</span>
                </button>
              </div>
            )}

            <UploadZone onAnalyze={handleStartAnalysis} isLoading={isLoading} />
          </>
        )}
      </div>
    </div>
  );
}
