import React from 'react';
import { Cpu, Info, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function MLClassificationCard({ mlAnalysis, forensicScore, forensicStatus }) {
  if (!mlAnalysis || !mlAnalysis.available) {
    return null;
  }

  const {
    prediction = 'authentic',
    signal_label,
    authentic_probability,
    manipulated_probability,
    confidence,
    model = 'EfficientNet-B0',
    model_version = 'pixelproof-casia-v1',
    explanation,
    disagreement,
    metrics = {}
  } = mlAnalysis;

  // Format probabilities cleanly
  const authPct = typeof authentic_probability === 'number'
    ? (authentic_probability * 100).toFixed(1)
    : (mlAnalysis.authentic_prob ? (mlAnalysis.authentic_prob * 100).toFixed(1) : '0.0');

  const manipPct = typeof manipulated_probability === 'number'
    ? (manipulated_probability * 100).toFixed(1)
    : (mlAnalysis.manipulated_prob ? (mlAnalysis.manipulated_prob * 100).toFixed(1) : '0.0');

  const isManipulated = String(prediction).toLowerCase() === 'manipulated';

  // Exact required wording:
  // "Manipulation-Leaning ML Signal" vs "Authenticity-Leaning ML Signal"
  const signalName = signal_label || (isManipulated ? 'Manipulation-Leaning ML Signal' : 'Authenticity-Leaning ML Signal');

  // Evidence Disagreement handling
  let hasDisagreement = false;
  let disagreementMessage = '';

  if (disagreement && disagreement.has_disagreement) {
    hasDisagreement = true;
    disagreementMessage = disagreement.message;
  } else if (forensicScore !== undefined && forensicScore !== null) {
    if (isManipulated && (forensicScore < 30 || forensicStatus === 'Low Suspicion')) {
      hasDisagreement = true;
      disagreementMessage =
        'The ML classifier detected manipulation-associated visual patterns, while classical forensic modules found limited direct manipulation evidence. Manual review is recommended when independent signals disagree.';
    } else if (!isManipulated && (forensicScore >= 60 || forensicStatus === 'Strong Manipulation Indicators')) {
      hasDisagreement = true;
      disagreementMessage =
        'Classical forensic modules detected strong manipulation indicators, while the ML classifier produced an authenticity-leaning visual pattern signal. Manual review is recommended when independent signals disagree.';
    } else if (!isManipulated && forensicScore >= 30) {
      hasDisagreement = true;
      disagreementMessage =
        'Classical forensic modules identified indicators warranting review, while the ML classifier produced an authenticity-leaning visual pattern signal. Manual review is recommended when independent signals disagree.';
    }
  }

  // Model benchmark metrics: CASIA 2.0 held-out test
  const accuracyPct = metrics.accuracy ? (metrics.accuracy * 100).toFixed(1) : '69.6';
  const f1Pct = metrics.f1_score ? (metrics.f1_score * 100).toFixed(1) : '68.0';
  const rocAucPct = metrics.roc_auc ? (metrics.roc_auc * 100).toFixed(1) : '76.4';
  const heldOutCount = metrics.held_out_test_images ? metrics.held_out_test_images.toLocaleString() : '1,893';

  return (
    <div className="card-white" style={{
      padding: '28px 32px',
      border: '1px solid #E2E8F0',
      borderRadius: '8px',
      backgroundColor: '#FFFFFF',
      marginBottom: '32px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '12px',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #F1F5F9'
      }}>
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: '#2563EB',
            marginBottom: '4px'
          }}>
            <Cpu size={14} />
            <span>Independent Machine-Learning Signal</span>
            <span style={{ color: '#94A3B8' }}>•</span>
            <span style={{ color: '#64748B', fontFamily: 'var(--font-mono)' }}>{model}</span>
          </div>

          <h3 style={{
            fontSize: '20px',
            fontWeight: 800,
            color: '#0F172A',
            letterSpacing: '-0.02em',
            margin: 0
          }}>
            MACHINE LEARNING CLASSIFICATION SIGNAL
          </h3>
        </div>

        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          padding: '6px 12px',
          borderRadius: '6px',
          backgroundColor: '#EFF6FF',
          border: '1px solid #BFDBFE',
          color: '#1D4ED8',
          fontSize: '12px',
          fontWeight: 700,
          fontFamily: 'var(--font-mono)'
        }}>
          <span>{model}</span>
          <span style={{ color: '#93C5FD' }}>|</span>
          <span style={{ color: '#2563EB' }}>{model_version}</span>
        </div>
      </div>

      {/* Clearly Visible Notice: ML is independent signal, not final forensic conclusion */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '10px 16px',
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '6px',
        fontSize: '13px',
        color: '#334155',
        marginBottom: hasDisagreement ? '16px' : '20px',
        lineHeight: 1.5
      }}>
        <Info size={16} color="#2563EB" style={{ flexShrink: 0 }} />
        <span>
          <strong>Notice: </strong>
          This is an independent machine-learning signal, not the final forensic conclusion.
        </span>
      </div>

      {/* 3. EVIDENCE DISAGREEMENT SECTION (Rendered when ML & forensics disagree) */}
      {hasDisagreement && (
        <div style={{
          backgroundColor: '#FFFBEB',
          border: '1.5px solid #FDE68A',
          borderRadius: '8px',
          padding: '16px 20px',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '12px'
        }}>
          <AlertTriangle size={20} color="#D97706" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{
              fontSize: '12px',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              color: '#B45309',
              marginBottom: '4px'
            }}>
              EVIDENCE DISAGREEMENT
            </div>
            <p style={{
              fontSize: '13px',
              color: '#92400E',
              margin: 0,
              lineHeight: 1.55
            }}>
              {disagreementMessage}
            </p>
          </div>
        </div>
      )}

      {/* Main Grid: Signal Classification & Model Probability */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        marginBottom: '20px'
      }}>
        {/* Left Column: Signal Classification */}
        <div style={{
          backgroundColor: isManipulated ? '#FEF2F2' : '#F0FDF4',
          border: `1px solid ${isManipulated ? '#FECACA' : '#BBF7D0'}`,
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            color: isManipulated ? '#991B1B' : '#166534',
            marginBottom: '8px'
          }}>
            Independent ML Signal
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '10px'
          }}>
            {isManipulated ? (
              <AlertTriangle size={22} color="#DC2626" style={{ flexShrink: 0 }} />
            ) : (
              <ShieldCheck size={22} color="#16A34A" style={{ flexShrink: 0 }} />
            )}
            <span style={{
              fontSize: '18px',
              fontWeight: 800,
              letterSpacing: '-0.01em',
              color: isManipulated ? '#DC2626' : '#15803D'
            }}>
              {signalName}
            </span>
          </div>

          <p style={{
            fontSize: '13px',
            color: isManipulated ? '#7F1D1D' : '#14532D',
            margin: '0 0 14px 0',
            lineHeight: 1.55
          }}>
            {explanation || (isManipulated
              ? 'Model detected visual patterns more consistent with manipulated imagery.'
              : 'Model detected visual patterns more consistent with authentic imagery.')}
          </p>

          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: '8px',
            paddingTop: '10px',
            borderTop: `1px solid ${isManipulated ? '#FCA5A5' : '#86EFAC'}`
          }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: '#475569' }}>
              Selected-class model probability:
            </span>
            <span style={{
              fontSize: '16px',
              fontWeight: 800,
              fontFamily: 'var(--font-mono)',
              color: isManipulated ? '#DC2626' : '#15803D'
            }}>
              {isManipulated ? manipPct : authPct}%
            </span>
          </div>
        </div>

        {/* Right Column: Model probability */}
        <div style={{
          backgroundColor: '#F8FAFC',
          border: '1px solid #E2E8F0',
          borderRadius: '8px',
          padding: '20px'
        }}>
          <div style={{
            fontSize: '13px',
            fontWeight: 700,
            color: '#0F172A',
            marginBottom: '16px'
          }}>
            Model probability:
          </div>

          {/* Manipulated probability row */}
          <div style={{ marginBottom: '18px' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              fontSize: '13px',
              marginBottom: '6px'
            }}>
              <span style={{ fontWeight: 600, color: '#0F172A' }}>Manipulated:</span>
              <span style={{
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: '#D97706'
              }}>
                {manipPct}%
              </span>
            </div>
            <div style={{
              height: '8px',
              backgroundColor: '#E2E8F0',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                backgroundColor: '#D97706',
                width: `${manipPct}%`,
                transition: 'width 0.6s ease'
              }} />
            </div>
          </div>

          {/* Authentic probability row */}
          <div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              fontSize: '13px',
              marginBottom: '6px'
            }}>
              <span style={{ fontWeight: 600, color: '#0F172A' }}>Authentic:</span>
              <span style={{
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: '#2563EB'
              }}>
                {authPct}%
              </span>
            </div>
            <div style={{
              height: '8px',
              backgroundColor: '#E2E8F0',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                backgroundColor: '#2563EB',
                width: `${authPct}%`,
                transition: 'width 0.6s ease'
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Grad-CAM Explainability: ML Influence Map */}
      {mlAnalysis.gradcam?.available && mlAnalysis.gradcam?.visualization && (
        <div style={{
          marginBottom: '20px',
          padding: '20px',
          backgroundColor: '#F8FAFC',
          border: '1px solid #E2E8F0',
          borderRadius: '8px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '8px',
            marginBottom: '12px'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: 700,
              color: '#0F172A',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>ML Influence Map</span>
              <span style={{
                fontSize: '11px',
                fontWeight: 600,
                color: '#2563EB',
                backgroundColor: '#EFF6FF',
                border: '1px solid #DBEAFE',
                padding: '2px 8px',
                borderRadius: '4px'
              }}>
                Target: {mlAnalysis.gradcam.target_class || prediction}
              </span>
            </div>
            <div style={{ fontSize: '11px', color: '#64748B' }}>
              Gradient-weighted Class Activation Mapping (Grad-CAM)
            </div>
          </div>

          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '20px',
            marginBottom: '12px'
          }}>
            <div style={{
              backgroundColor: '#0F172A',
              padding: '8px',
              borderRadius: '6px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <img
                src={mlAnalysis.gradcam.visualization}
                alt="ML Influence Map (Grad-CAM)"
                style={{
                  maxWidth: '100%',
                  maxHeight: '260px',
                  objectFit: 'contain',
                  borderRadius: '4px',
                  display: 'block'
                }}
              />
            </div>
          </div>

          <div style={{
            fontSize: '12px',
            color: '#475569',
            lineHeight: 1.5,
            display: 'flex',
            alignItems: 'flex-start',
            gap: '6px'
          }}>
            <Info size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#2563EB' }} />
            <span>
              <strong>Scientific interpretation:</strong> {mlAnalysis.gradcam.explanation || "Highlighted regions contributed more strongly to the model's selected classification."}
              {" "}<em>This visualization indicates regions that influenced the ML classifier. It does not identify confirmed manipulated pixels.</em>
            </span>
          </div>
        </div>
      )}

      {/* 4. MODEL BENCHMARK SECTION */}
      <div style={{
        marginTop: '8px',
        padding: '16px 20px',
        backgroundColor: '#F8FAFC',
        border: '1px solid #E2E8F0',
        borderRadius: '8px'
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
          color: '#475569',
          marginBottom: '12px'
        }}>
          Model Benchmark & Dataset Specifications
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '12px',
          marginBottom: '12px'
        }}>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>Architecture</div>
            <div style={{ fontSize: '13px', color: '#0F172A', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{model}</div>
          </div>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>Dataset</div>
            <div style={{ fontSize: '13px', color: '#0F172A', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>CASIA 2.0</div>
          </div>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>Held-out test</div>
            <div style={{ fontSize: '13px', color: '#0F172A', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{heldOutCount} images</div>
          </div>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>Accuracy</div>
            <div style={{ fontSize: '13px', color: '#2563EB', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{accuracyPct}%</div>
          </div>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>F1</div>
            <div style={{ fontSize: '13px', color: '#2563EB', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{f1Pct}%</div>
          </div>
          <div style={{ padding: '8px 12px', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '6px' }}>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600 }}>ROC-AUC</div>
            <div style={{ fontSize: '13px', color: '#2563EB', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{rocAucPct}%</div>
          </div>
        </div>

        <div style={{
          fontSize: '12px',
          color: '#64748B',
          lineHeight: 1.5,
          display: 'flex',
          alignItems: 'flex-start',
          gap: '6px'
        }}>
          <Info size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#2563EB' }} />
          <span>
            <strong>Dataset benchmark note:</strong> These metrics reflect measured generalization on {heldOutCount} held-out test images in the CASIA 2.0 dataset, <em>not</em> confidence for the currently uploaded image.
          </span>
        </div>
      </div>
    </div>
  );
}
