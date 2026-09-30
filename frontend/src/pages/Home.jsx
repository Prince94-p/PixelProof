import React from 'react';
import { 
  Scan, ShieldCheck, ArrowRight, Activity, Copy, Layers, 
  Fingerprint, FileCheck, CheckCircle2, AlertTriangle, Eye, 
  HelpCircle, ChevronRight, Lock, Sparkles
} from 'lucide-react';

export default function Home({ setCurrentPage }) {
  const modules = [
    {
      num: '01',
      title: 'Metadata Analysis',
      subtitle: 'EXIF & Camera Hardware Tags',
      desc: 'Inspects camera manufacturer tags, timestamps, software signatures (e.g. Adobe Photoshop, GIMP), and container metadata traces.',
      tag: 'Provenential'
    },
    {
      num: '02',
      title: 'Error Level Analysis',
      subtitle: '90% DCT Recompression Delta',
      desc: 'Recompresses the image to identify localized compression variance. Spliced elements saved at differing rates reveal distinct error levels.',
      tag: 'Mathematical'
    },
    {
      num: '03',
      title: 'Copy-Move Detection',
      subtitle: 'ORB Feature Displacement Vectors',
      desc: 'Detects duplicated regions by matching high-dimensional texture keypoints and clustering coherent spatial displacement vectors.',
      tag: 'Geometric'
    },
    {
      num: '04',
      title: 'Noise Consistency',
      subtitle: 'Local Residual Variance Heatmap',
      desc: 'Extracts high-frequency sensor noise residuals to discover local noise floor anomalies, spliced regions, or retouching blurs.',
      tag: 'Statistical'
    },
    {
      num: '05',
      title: 'Digital Fingerprint',
      subtitle: 'Cryptographic SHA-256 Hashing',
      desc: 'Generates an immutable cryptographic fingerprint of exact image bytes for integrity auditing and chain-of-custody tracking.',
      tag: 'Cryptographic'
    }
  ];

  return (
    <div style={{ backgroundColor: '#FFFFFF' }}>
      {/* ============================================================
          HERO SECTION (STRICT LIGHT THEME)
          ============================================================ */}
      <section className="tech-grid-bg" style={{
        borderBottom: '1px solid #E2E8F0',
        padding: '72px 0 88px 0',
        position: 'relative'
      }}>
        <div className="container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '56px',
            alignItems: 'center'
          }}>
            {/* Left Column: Headlines & Call to Action */}
            <div>
              {/* Badge */}
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#EFF6FF',
                color: '#2563EB',
                border: '1px solid #DBEAFE',
                padding: '6px 14px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 700,
                letterSpacing: '0.06em',
                marginBottom: '20px',
                boxShadow: '0 1px 2px rgba(37, 99, 235, 0.08)'
              }}>
                <Scan size={15} />
                <span>DIGITAL IMAGE FORENSICS</span>
              </div>

              {/* Main Headline */}
              <h1 style={{
                fontSize: 'clamp(38px, 5vw, 56px)',
                fontWeight: 800,
                color: '#0F172A',
                letterSpacing: '-0.03em',
                lineHeight: '1.15',
                marginBottom: '20px'
              }}>
                Don't trust the image.<br />
                <span style={{ color: '#1D4ED8' }}>Verify the evidence.</span>
              </h1>

              {/* Description */}
              <p style={{
                fontSize: '17px',
                lineHeight: '1.65',
                color: '#475569',
                marginBottom: '36px',
                maxWidth: '540px'
              }}>
                PixelProof combines multiple digital forensic techniques to identify potential image manipulation and explain the evidence behind every result.
              </p>

              {/* Action Buttons */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '14px',
                marginBottom: '36px'
              }}>
                <button
                  onClick={() => { setCurrentPage('analyze'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  className="btn-primary"
                  style={{
                    padding: '14px 28px',
                    fontSize: '16px'
                  }}
                  id="hero-analyze-btn"
                >
                  <ShieldCheck size={20} />
                  <span>Analyze an Image</span>
                  <ArrowRight size={18} />
                </button>

                <button
                  onClick={() => { setCurrentPage('how-it-works'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  className="btn-secondary"
                  style={{
                    padding: '14px 24px',
                    fontSize: '16px'
                  }}
                >
                  See How It Works
                </button>
              </div>

              {/* Trust Indicators */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '24px',
                fontSize: '13px',
                color: '#64748B',
                borderTop: '1px solid #E2E8F0',
                paddingTop: '20px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} style={{ color: '#15803D' }} />
                  <span>100% Real Analysis</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} style={{ color: '#15803D' }} />
                  <span>Transparent Scoring</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle2 size={16} style={{ color: '#15803D' }} />
                  <span>No Fake Results</span>
                </div>
              </div>
            </div>

            {/* Right Column: Hero Visual Forensic Workbench Mockup */}
            <div style={{ position: 'relative' }}>
              <div className="card-white" style={{
                padding: '24px',
                borderRadius: '16px',
                border: '1px solid #CBD5E1',
                boxShadow: '0 20px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)',
                backgroundColor: '#FFFFFF',
                position: 'relative'
              }}>
                {/* Workbench Top Header */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  borderBottom: '1px solid #E2E8F0',
                  paddingBottom: '14px',
                  marginBottom: '16px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#2563EB' }} />
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A', fontFamily: 'var(--font-mono)' }}>
                      FORENSIC_CANVAS_SPLIT.VIEW
                    </span>
                  </div>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: '#0891B2',
                    backgroundColor: '#ECFEFF',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    border: '1px solid #CFFAFE'
                  }}>
                    LIVE EVIDENCE ENGINE
                  </span>
                </div>

                {/* Side by side comparison canvas */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px',
                  height: '240px',
                  position: 'relative',
                  marginBottom: '16px'
                }}>
                  {/* Left: Original Image simulation */}
                  <div style={{
                    backgroundColor: '#F1F5F9',
                    borderRadius: '8px',
                    border: '1px solid #E2E8F0',
                    padding: '12px',
                    position: 'relative',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: '#475569',
                      backgroundColor: 'rgba(255,255,255,0.9)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      width: 'fit-content'
                    }}>
                      ORIGINAL IMAGE
                    </span>

                    {/* Technical coordinate marks */}
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                      color: '#94A3B8'
                    }}>
                      <div style={{
                        width: '80px',
                        height: '80px',
                        border: '1px dashed #94A3B8',
                        borderRadius: '6px',
                        margin: '0 auto',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '11px',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        RGB INPUT
                      </div>
                    </div>

                    <div style={{
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      color: '#64748B'
                    }}>
                      RES: 1920×1080 • sRGB
                    </div>
                  </div>

                  {/* Right: Forensic Scan simulation */}
                  <div style={{
                    backgroundColor: '#EFF6FF',
                    borderRadius: '8px',
                    border: '1.5px solid #93C5FD',
                    padding: '12px',
                    position: 'relative',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      color: '#2563EB',
                      backgroundColor: 'rgba(255,255,255,0.9)',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      width: 'fit-content'
                    }}>
                      FORENSIC SCAN
                    </span>

                    {/* Scan Line effect */}
                    <div className="scan-line" />

                    {/* Simulated detection bounding box */}
                    <div style={{
                      position: 'absolute',
                      top: '40px',
                      right: '24px',
                      width: '70px',
                      height: '60px',
                      border: '2px solid #2563EB',
                      backgroundColor: 'rgba(37, 99, 235, 0.08)',
                      borderRadius: '4px'
                    }}>
                      <span style={{
                        fontSize: '9px',
                        fontWeight: 700,
                        backgroundColor: '#2563EB',
                        color: '#FFFFFF',
                        padding: '1px 3px',
                        borderRadius: '2px',
                        position: 'absolute',
                        top: '-12px',
                        left: '-2px',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        Δ ELA +24%
                      </span>
                    </div>

                    <div style={{
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      color: '#2563EB',
                      fontWeight: 600
                    }}>
                      RECOMPRESSION VARIANCE: DETECTED
                    </div>
                  </div>
                </div>

                {/* Floating Technical Engine Badges */}
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px',
                  paddingTop: '12px',
                  borderTop: '1px solid #E2E8F0'
                }}>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: '#F1F5F9',
                    color: '#0F172A',
                    border: '1px solid #CBD5E1',
                    padding: '4px 10px',
                    borderRadius: '6px'
                  }}>
                    ELA ANALYSIS
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: '#F1F5F9',
                    color: '#0F172A',
                    border: '1px solid #CBD5E1',
                    padding: '4px 10px',
                    borderRadius: '6px'
                  }}>
                    COPY-MOVE
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: '#F1F5F9',
                    color: '#0F172A',
                    border: '1px solid #CBD5E1',
                    padding: '4px 10px',
                    borderRadius: '6px'
                  }}>
                    METADATA
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: '#F1F5F9',
                    color: '#0F172A',
                    border: '1px solid #CBD5E1',
                    padding: '4px 10px',
                    borderRadius: '6px'
                  }}>
                    SHA-256
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================
          SECTION 2: FORENSIC MODULES (5 CARDS)
          ============================================================ */}
      <section style={{
        padding: '80px 0',
        backgroundColor: '#F8FAFC',
        borderBottom: '1px solid #E2E8F0'
      }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '720px', margin: '0 auto 48px auto' }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#2563EB',
              marginBottom: '8px'
            }}>
              Multi-Layered Verification Architecture
            </div>
            <h2 style={{
              fontSize: 'clamp(28px, 4vw, 38px)',
              fontWeight: 800,
              color: '#0F172A',
              letterSpacing: '-0.02em',
              marginBottom: '14px'
            }}>
              ONE IMAGE. MULTIPLE LAYERS OF EVIDENCE.
            </h2>
            <p style={{ fontSize: '16px', color: '#64748B', lineHeight: '1.6' }}>
              Manipulation rarely hides across all forensic domains simultaneously. 
              PixelProof performs independent physical, mathematical, and cryptographic cross-checks.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '24px'
          }}>
            {modules.map((m) => (
              <div
                key={m.num}
                className="card-white"
                style={{
                  padding: '28px',
                  borderRadius: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  border: '1px solid #E2E8F0',
                  boxShadow: '0 2px 4px rgba(15, 23, 42, 0.03)'
                }}
              >
                <div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '16px'
                  }}>
                    <span style={{
                      fontSize: '18px',
                      fontWeight: 800,
                      color: '#2563EB',
                      fontFamily: 'var(--font-mono)'
                    }}>
                      {m.num}
                    </span>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: '#0891B2',
                      backgroundColor: '#ECFEFF',
                      border: '1px solid #CFFAFE',
                      padding: '3px 8px',
                      borderRadius: '4px'
                    }}>
                      {m.tag}
                    </span>
                  </div>

                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: 700,
                    color: '#0F172A',
                    marginBottom: '4px'
                  }}>
                    {m.title}
                  </h3>
                  <div style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: '#64748B',
                    marginBottom: '12px'
                  }}>
                    {m.subtitle}
                  </div>
                  <p style={{
                    fontSize: '14px',
                    lineHeight: '1.6',
                    color: '#475569'
                  }}>
                    {m.desc}
                  </p>
                </div>

                <div style={{
                  marginTop: '20px',
                  paddingTop: '16px',
                  borderTop: '1px solid #F1F5F9',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px',
                  fontWeight: 600,
                  color: '#2563EB'
                }}>
                  <span>Autonomous Engine</span>
                  <CheckCircle2 size={14} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================================
          SECTION 3: HOW IT WORKS PIPELINE PREVIEW
          ============================================================ */}
      <section style={{
        padding: '80px 0',
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0'
      }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '48px', maxWidth: '640px', margin: '0 auto 48px auto' }}>
            <h2 style={{
              fontSize: '32px',
              fontWeight: 800,
              color: '#0F172A',
              marginBottom: '12px'
            }}>
              Forensic Verification Pipeline
            </h2>
            <p style={{ fontSize: '15px', color: '#64748B' }}>
              From initial upload to explainable evidentiary report in 5 continuous stages
            </p>
          </div>

          {/* Pipeline flow */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '16px',
            alignItems: 'center'
          }}>
            {[
              { step: '1', title: 'UPLOAD', desc: 'Secure bytes check & container decode' },
              { step: '2', title: 'ANALYZE', desc: '5 independent forensic computations' },
              { step: '3', title: 'CROSS-CHECK', desc: 'Multi-module corroboration' },
              { step: '4', title: 'VISUALIZE', desc: 'Comparative forensic overlays' },
              { step: '5', title: 'EXPLAIN', desc: 'Initial evidence score & report' },
            ].map((p, idx) => (
              <div key={p.step} style={{
                backgroundColor: '#F8FAFC',
                border: '1.5px solid #DBEAFE',
                borderRadius: '12px',
                padding: '24px 18px',
                textAlign: 'center',
                position: 'relative'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: '#2563EB',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 12px auto'
                }}>
                  {p.step}
                </div>
                <h4 style={{ fontSize: '15px', fontWeight: 800, color: '#0F172A', marginBottom: '6px' }}>
                  {p.title}
                </h4>
                <p style={{ fontSize: '12px', color: '#64748B', lineHeight: '1.5' }}>
                  {p.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============================================================
          SECTION 4: KEY DIFFERENTIATOR CALLOUT
          ============================================================ */}
      <section style={{
        padding: '72px 0',
        backgroundColor: '#F1F5F9'
      }}>
        <div className="container">
          <div className="card-white" style={{
            padding: '48px 36px',
            borderRadius: '16px',
            border: '1px solid #CBD5E1',
            textAlign: 'center',
            maxWidth: '860px',
            margin: '0 auto'
          }}>
            <span style={{
              fontSize: '12px',
              fontWeight: 800,
              textTransform: 'uppercase',
              color: '#2563EB',
              letterSpacing: '0.08em',
              backgroundColor: '#EFF6FF',
              padding: '4px 12px',
              borderRadius: '20px',
              border: '1px solid #DBEAFE'
            }}>
              Explainable Forensic Standard
            </span>

            <h3 style={{
              fontSize: '28px',
              fontWeight: 800,
              color: '#0F172A',
              margin: '16px 0 12px 0',
              letterSpacing: '-0.02em'
            }}>
              PixelProof does not blindly label an image as real or fake.
            </h3>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.6',
              color: '#475569',
              marginBottom: '28px',
              maxWidth: '680px',
              margin: '0 auto 28px auto'
            }}>
              Black-box AI classifiers output opaque percentages without justification. 
              PixelProof puts the technical evidence directly in your hands—revealing the exact recompression boundaries, duplicated keypoints, sensor noise gradients, and container tags.
            </p>

            <button
              onClick={() => { setCurrentPage('analyze'); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
              className="btn-primary"
              style={{ padding: '14px 32px', fontSize: '16px' }}
            >
              <ShieldCheck size={20} />
              <span>Launch Forensic Analysis</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
