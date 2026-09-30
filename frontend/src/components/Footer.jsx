import React from 'react';
import { Scan, ShieldCheck, ExternalLink, Cpu, FileText } from 'lucide-react';

export default function Footer({ setCurrentPage }) {
  return (
    <footer style={{
      backgroundColor: '#F8FAFC',
      borderTop: '1px solid #E2E8F0',
      padding: '48px 0 36px 0',
      color: '#475569',
      marginTop: 'auto'
    }}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '36px',
          marginBottom: '36px'
        }}>
          {/* Col 1: Brand & Tagline */}
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '14px'
            }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                backgroundColor: '#EFF6FF',
                border: '1.5px solid #DBEAFE',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#2563EB'
              }}>
                <Scan size={18} strokeWidth={2.4} />
              </div>
              <span style={{
                fontWeight: 800,
                fontSize: '19px',
                color: '#0F172A',
                letterSpacing: '-0.02em'
              }}>
                Pixel<span style={{ color: '#2563EB' }}>Proof</span>
              </span>
            </div>
            <p style={{
              fontSize: '14px',
              lineHeight: '1.6',
              color: '#64748B',
              marginBottom: '16px'
            }}>
              Don't trust the image. Verify the evidence. An explainable digital image forensics platform analyzing metadata, recompression anomalies, cloning traces, and local sensor noise.
            </p>
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '12px',
              fontWeight: 600,
              color: '#0891B2',
              backgroundColor: '#ECFEFF',
              border: '1px solid #CFFAFE',
              padding: '4px 10px',
              borderRadius: '6px'
            }}>
              <Cpu size={14} />
              <span>Problem Statement #22 — Cybersecurity / AI</span>
            </div>
          </div>

          {/* Col 2: Navigation Links */}
          <div>
            <h4 style={{
              fontSize: '14px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#0F172A',
              marginBottom: '16px'
            }}>
              Platform
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li>
                <button
                  onClick={() => { setCurrentPage('analyze'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    fontSize: '14px',
                    color: '#475569',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.color = '#2563EB'}
                  onMouseLeave={(e) => e.target.style.color = '#475569'}
                >
                  Forensic Image Analysis
                </button>
              </li>
              <li>
                <button
                  onClick={() => { setCurrentPage('how-it-works'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    fontSize: '14px',
                    color: '#475569',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.color = '#2563EB'}
                  onMouseLeave={(e) => e.target.style.color = '#475569'}
                >
                  How It Works & Methodology
                </button>
              </li>
              <li>
                <button
                  onClick={() => { setCurrentPage('home'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: 0,
                    fontSize: '14px',
                    color: '#475569',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.color = '#2563EB'}
                  onMouseLeave={(e) => e.target.style.color = '#475569'}
                >
                  Forensic Architecture Overview
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Forensic Modules */}
          <div>
            <h4 style={{
              fontSize: '14px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: '#0F172A',
              marginBottom: '16px'
            }}>
              Forensic Engines
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px', color: '#64748B' }}>
              <li>• Error Level Analysis (ELA 90% DCT)</li>
              <li>• ORB Feature Copy-Move Detection</li>
              <li>• Local Residual Noise Consistency</li>
              <li>• EXIF & Camera Software Forensics</li>
              <li>• SHA-256 Cryptographic Fingerprint</li>
            </ul>
          </div>
        </div>

        {/* Forensic Disclaimer */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '14px 18px',
          marginBottom: '28px',
          fontSize: '12px',
          lineHeight: '1.6',
          color: '#64748B'
        }}>
          <strong style={{ color: '#0F172A' }}>Forensic Investigative Notice:</strong> PixelProof performs objective mathematical and statistical forensic measurements. While anomalies highlight areas of potential tampering, findings should be evaluated with image provenance, compression context, and technical domain review.
        </div>

        {/* Bottom row */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingTop: '20px',
          borderTop: '1px solid #E2E8F0',
          fontSize: '13px',
          color: '#64748B'
        }}>
          <div>
            © {new Date().getFullYear()} PixelProof Forensics. Built for Problem Statement #22.
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <span>Verified Local Forensic Engine</span>
            <span>•</span>
            <span>OpenCV + Pillow + NumPy</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
