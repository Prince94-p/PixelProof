import React, { useState, useEffect } from 'react';
import { CheckCircle2, Circle, Loader2, Scan, Shield } from 'lucide-react';

export default function LoadingAnalysis({ previewUrl, filename }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const steps = [
    { label: 'Validating container structure & decoding image bytes' },
    { label: 'Extracting EXIF metadata & software signatures' },
    { label: 'Running Error Level Analysis (90% DCT recompression)' },
    { label: 'Searching for copy-move duplicated feature clusters' },
    { label: 'Analyzing high-frequency local noise consistency' },
    { label: 'Cross-checking forensic indicators & computing score' }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 700);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ maxWidth: '780px', margin: '40px auto 0 auto' }}>
      <div className="card-white" style={{
        padding: '36px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(15, 23, 42, 0.06)'
      }}>
        {/* Title */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#EFF6FF',
            color: '#2563EB',
            border: '1px solid #DBEAFE',
            padding: '6px 14px',
            borderRadius: '20px',
            fontSize: '13px',
            fontWeight: 700,
            marginBottom: '12px'
          }}>
            <Scan size={16} className="pulse-dot" />
            <span>FORENSIC PIPELINE ACTIVE</span>
          </div>

          <h2 style={{
            fontSize: '24px',
            fontWeight: 800,
            color: '#0F172A',
            letterSpacing: '-0.02em',
            marginBottom: '6px'
          }}>
            Analyzing Image Authenticity
          </h2>
          <p style={{ fontSize: '14px', color: '#64748B' }}>
            Executing independent digital-forensic tests on <strong style={{ color: '#0F172A' }}>{filename}</strong>
          </p>
        </div>

        {/* Content layout: Preview on left (or top), Step checklist on right */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '28px',
          alignItems: 'center',
          marginBottom: '28px'
        }}>
          {/* Image Preview with Scan Line */}
          <div style={{
            position: 'relative',
            backgroundColor: '#F8FAFC',
            border: '1px solid #CBD5E1',
            borderRadius: '10px',
            overflow: 'hidden',
            height: '240px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Scanning preview"
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain'
                }}
              />
            )}
            {/* Animated Laser Scan Line */}
            <div className="scan-line" />

            <div style={{
              position: 'absolute',
              bottom: '10px',
              left: '12px',
              backgroundColor: 'rgba(255, 255, 255, 0.92)',
              backdropFilter: 'blur(4px)',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 700,
              color: '#2563EB',
              border: '1px solid #DBEAFE',
              fontFamily: 'var(--font-mono)'
            }}>
              SCANNING 100% BYTE STREAM
            </div>
          </div>

          {/* Sequential Forensic Checklist */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '14px'
          }}>
            {steps.map((step, idx) => {
              const isCompleted = idx < currentStepIndex;
              const isCurrent = idx === currentStepIndex;

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    fontSize: '14px',
                    transition: 'all 0.2s ease',
                    color: isCompleted ? '#0F172A' : (isCurrent ? '#2563EB' : '#94A3B8'),
                    fontWeight: isCurrent ? 700 : (isCompleted ? 600 : 400)
                  }}
                >
                  {isCompleted ? (
                    <CheckCircle2 size={18} style={{ color: '#15803D', flexShrink: 0 }} />
                  ) : isCurrent ? (
                    <Loader2 size={18} className="spin" style={{ color: '#2563EB', flexShrink: 0 }} />
                  ) : (
                    <Circle size={18} style={{ color: '#CBD5E1', flexShrink: 0 }} />
                  )}
                  <span>{step.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Progress Bar */}
        <div>
          <div style={{
            height: '6px',
            backgroundColor: '#EFF6FF',
            borderRadius: '3px',
            overflow: 'hidden',
            border: '1px solid #DBEAFE'
          }}>
            <div style={{
              height: '100%',
              backgroundColor: '#2563EB',
              borderRadius: '3px',
              width: `${Math.min(95, ((currentStepIndex + 1) / steps.length) * 100)}%`,
              transition: 'width 0.5s ease'
            }} />
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
